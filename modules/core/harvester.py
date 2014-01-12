import configparser
from threading import Timer
from modules.utils.config import config

from modules.network.http_request_high_level import download_file
from modules.utils.decompression import decompression_gz

from modules.boinc.stat_file_operation import search_team_in_file_by_name

from modules.database.boinc_mongo import (register_team_state_in_database,
                                          register_stats_state_in_database)
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
        configurator = configparser.ConfigParser()
        configurator.read("../../harvest.config")
        #configurator.read("harvest.config")
        self.projects = {}
        for project in configurator.sections():
            self.projects[project] = {}
            for key in configurator[project]:
                self.projects[project][key] = configurator[project][key]
        for project in self.projects:
            try:
                self.projects[project]["frequency"] = int(self.projects[project]["frequency"])
                self.projects[project]["ETA"] = 0
            except KeyError:
                self.projects[project]["frequency"] = 6000
                self.projects[project]["ETA"] = 0
        self.interval = 10
        self.my_pool_of_processes = Pool(int(config["ASFBAH"]["CPU_CORE_TO_USE_FOR_HARVESTING"]))
        self.refresh = None
        self.check_state_timer()

    def update_configuration(self):
        configurator = configparser.ConfigParser()
        configurator.read("../../harvest.config")
        for project in configurator.sections():
            try:
                for key in configurator[project]:
                    self.projects[project][key] = configurator[project][key]
                try:
                    self.projects[project]["frequency"] = int(self.projects[project]["frequency"])
                except KeyError:
                    self.projects[project]["frequency"] = 6000
            except KeyError:
                self.projects[project] = {}
                for key in configurator[project]:
                    self.projects[project][key] = configurator[project][key]
                try:
                    self.projects[project]["frequency"] = int(self.projects[project]["frequency"])
                except KeyError:
                    self.projects[project]["frequency"] = 6000

    def write_report(self):
        file_to_write = open(config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + "harvester_report", 'w')
        file_to_write.write(str(self))
        file_to_write.close()

    def check_state_timer(self):
        parameters = []

        for project in self.projects:
            self.projects[project]["ETA"] -= self.interval
            if self.projects[project]["ETA"] <= 0:
                print(str(project) + " is ready to be harvested")
                self.projects[project]["ETA"] = self.projects[project]["frequency"]
                parameters.append((self.projects[project]["name"], self.projects[project]["url"]))

        if parameters:
            self.my_pool_of_processes.starmap(process_project_stats, parameters)
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.update_configuration()
        self.refresh.start()

    def stop(self):
        self.refresh.cancel()
        self.my_pool_of_processes.close()

    def start(self):
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()

    def __str__(self):
        return str(self.projects)


def process_project_user(name, url):
    file_to_extract = download_file(url + "team.gz", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + sep +
                                                     "team.gz")
    file_pr = decompression_gz(file_to_extract, False)
    team = search_team_in_file_by_name(file_pr, config["ASFBAH"]["TEAM"])
    register_team_state_in_database(team, name)


def process_project_stats(name, url):
    from modules.database.logging import log_something_harvester

    try:
        import time
        start = time.time()
        log_something_harvester(name, "TYPE_INFO", "Downloading ... ")
        file_to_extract = download_file(url + "team.gz", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + sep +
                                                         "team.gz")
        log_something_harvester(name, "TYPE_INFO", "Extracting ... ")
        file_pr = decompression_gz(file_to_extract, False)
        log_something_harvester(name, "TYPE_INFO", "Looking for "+ config["ASFBAH"]["TEAM"] + " data ... ")
        team = search_team_in_file_by_name(file_pr, config["ASFBAH"]["TEAM"])
        log_something_harvester(name, "TYPE_INFO", "Injecting into database ... ")
        register_stats_state_in_database(team, name)
        elapsed = (time.time() - start)
        log_something_harvester(name, "TYPE_INFO", "Complete in " + str(elapsed) + "sec")
    except Exception as e:
        log_something_harvester(name, "TYPE_ERROR", e.__repr__())
