import time

from threading import Timer
from modules.utils.config import config
from modules.network.http_request_high_level import download_file
from modules.utils.decompression import decompression_gz
from modules.boinc.stat_file_operation import (search_team_in_file_by_name,
                                               db_tables_data_extraction,
                                               db_dump_data_extraction
                                               )
from modules.database.logging import log_something_harvester
from modules.database.boinc_mongo import (register_stats_state_in_database,
                                          get_all_project,
                                          update_projects_harvest_time
                                          )
from os import sep
from multiprocessing.pool import Pool


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Harvester(object, metaclass=Singleton):
    def __init__(self):

        projects_from_mongo = get_all_project()
        self._projects = []
        for project in projects_from_mongo:
            if not "name" in project or not "url" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR",
                                        "A project without name or url in database, skipped ...")
            else:
                if not project["frequency"]:
                    project["frequency"] = 6000
                    project["ETA"] = 6000
                else:
                    project["ETA"] = project["frequency"]
                self._projects.append(project)

        self.interval = 60
        self.my_pool_of_processes = Pool(int(config["ASFBAH"]["CPU_CORE_TO_USE_FOR_HARVESTING"]))
        self.refresh = None
        self.check_state_timer()

    def update_configuration(self):
        projects_from_mongo = get_all_project()
        for project in projects_from_mongo:
            if not "name" in project or not "url" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR",
                                        "A project without name or url in database, skipped ...")
            else:
                if not project["name"] in self._projects:
                    if not project["frequency"]:
                        project["frequency"] = 6000
                        project["ETA"] = 6000
                    else:
                        project["ETA"] = project["frequency"]
                    self._projects.append(project)

    def check_state_timer(self):
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()

        parameters = []
        for project in self._projects:
            project["ETA"] -= self.interval
            if project["ETA"] <= 0:
                project["ETA"] = project["frequency"]
                parameters.append((project["name"], project["url"], project["last_time_harvested"]))
        if parameters:
            self.my_pool_of_processes.starmap(process_project_stats, parameters)
        self.update_configuration()

    def stop(self):
        self.refresh.cancel()
        self.my_pool_of_processes.close()

    def start(self):
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()

    def __str__(self):
        return str(self._projects)

def process_project_stats(name, url, last_time_harvested):
    try:
        import time

        log_something_harvester(name, "TYPE_START", "STARTING ... ")
        start = time.time()
        log_something_harvester(name, "TYPE_INFO", "Downloading tables.xml... ")
        table_xml = download_file(url + "tables.xml", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + sep +
                                                      "tables.xml")
        log_something_harvester(name, "TYPE_INFO", "Processing tables.xml... ")
        info_table_xml = db_tables_data_extraction("", table_xml)
        if (last_time_harvested and last_time_harvested < info_table_xml["last_update"]) or (not last_time_harvested):
            log_something_harvester(name, "TYPE_INFO", "Downloading db_dump.xml ... ")
            dump_xml = download_file(url + "db_dump.xml", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + sep +
                                                          "db_dump.xml")
            log_something_harvester(name, "TYPE_INFO", "Processing db_dump.xml ... ")
            files_to_download = db_dump_data_extraction("", dump_xml)
            log_something_harvester(name, "TYPE_INFO", "Downloading team file... ")
            file_to_extract = download_file(url + files_to_download["team"] + ".gz",
                                            config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + sep +
                                            "team.gz")
            log_something_harvester(name, "TYPE_INFO", "Extracting ... ")
            file_pr = decompression_gz(file_to_extract, False)
            log_something_harvester(name, "TYPE_INFO", "Looking for " + config["ASFBAH"]["TEAM"] + " data ... ")
            team = search_team_in_file_by_name(file_pr, config["ASFBAH"]["TEAM"])
            log_something_harvester(name, "TYPE_INFO", "Injecting into database ... ")
            register_stats_state_in_database(team, name)
            update_projects_harvest_time(name)
            elapsed = (time.time() - start)
            log_something_harvester(name, "TYPE_COMPLETE", "Complete in " + str(round(elapsed, 3)) + " sec")

        else:
            log_something_harvester(name, "TYPE_COMPLETE", "Already up-to-date")
    except Exception as e:
        log_something_harvester(name, "TYPE_ERROR", e.__repr__())
