from threading import Timer
from multiprocessing.pool import Pool

from modules.utils.config import config

from modules.database.logging import log_something_harvester
from modules.database.boinc_mongo import (get_all_project
                                          )


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
        try:
            for project in self._projects:
                project["ETA"] -= self.interval
                if project["ETA"] <= 0:
                    project["ETA"] = project["frequency"]
                    parameters = ()
                    for arg in project["function"].__code__.co_varnames:
                        parameters += (project[arg])
                    self.my_pool_of_processes.starmap(project["function"], parameters)
        except Exception as e:
            log_something_harvester("Harvester", "TYPE_ERROR", repr(e))
        self.update_configuration()

    def stop(self):
        self.refresh.cancel()
        self.my_pool_of_processes.close()

    def start(self):
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()

    def __str__(self):
        return str(self._projects)
