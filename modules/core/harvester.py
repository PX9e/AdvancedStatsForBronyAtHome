# coding=utf-8

from threading import Timer
from multiprocessing.pool import Pool
from importlib import import_module
from modules.utils.config import config
from modules.database.logging import log_something_harvester
from modules.database.boinc_mongo import get_all_project


class Singleton(type):
    """
        This class allows the creation of singleton,
        it is used to make Harvester as a singleton, it could
        be useful in the future, when we will add remote control
        of the Harvester.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class Harvester(object, metaclass=Singleton):
    """
    *Main class for harvesting.*

    This class is the class which do all the harvesting part
    it will look into the database to find the differents project.
    And then run a process with the specified harvesting function and
    parameters specified in the database.

    We can have only one Harvester at the same time, that's why it is
    a singleton.
    """
    def __init__(self):
        projects_from_mongo = get_all_project()
        self._projects = []
        self._projects_name = []
        self._cycle_number = 0
        for project in projects_from_mongo:
            if not "name" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR",
                                        "A project without name in database " +
                                        str(project._id) + ", skipped ...")
            else:
                print("initial add " + str(project["name"]))
                if not project["frequency"]:
                    project["frequency"] = 3600
                    project["ETA"] = 0
                else:
                    try:
                        project["frequency"] = int(project["frequency"])
                        project["ETA"] = 0
                    except (TypeError, ValueError):
                        project["frequency"] = 3600
                        project["ETA"] = 0
                self._projects.append(project)
                self._projects_name.append(project["name"])
        self.interval = int(config["ASFBAH"]["REFRESH_RATE"])
        self.my_pool_of_processes = Pool(
            int(config["ASFBAH"]["CPU_CORE_TO_USE_FOR_HARVESTING"]))
        self.refresh = None
        self.check_state_timer()
        
    def update_configuration(self):
        projects_from_mongo = get_all_project()
        for project in projects_from_mongo:
            if not "name" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR",
                                        "A project without name in database "
                                        + str(project._id) + ", skipped ...")
            else:
                if not project["name"] in self._projects_name:
                    print("refresh add " + str(project["name"]))
                    if not project["frequency"]:
                        project["frequency"] = 3600
                        project["ETA"] = 0
                    else:
                        try:
                            project["frequency"] = int(project["frequency"])
                            project["ETA"] = 0
                        except (TypeError, ValueError):
                            project["frequency"] = 3600
                            project["ETA"] = 0
                    self._projects.append(project)
                    self._projects_name.append(project["name"])

    def check_state_timer(self):
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()
        del self.refresh
        try:
            for project in self._projects:
                print("analyzing: " + project["name"] + " ETA: " + str(
                    project["ETA"]))
                project["ETA"] -= self.interval
                if project["ETA"] <= 0:
                    project["ETA"] = int(project["frequency"])
                    parameters = ()
                    function_to_run = getattr(
                        import_module("modules.core.harvesting_function"),
                        project["harvesting_function"])
                    variables_for_process = \
                        function_to_run.__code__.co_varnames[
                        :function_to_run.__code__.co_argcount]
                    for arg in variables_for_process:
                        parameters += (project[arg],)
                    parameters = ((parameters,))
                    self.my_pool_of_processes.starmap_async(function_to_run,
                                                            parameters)
        except Exception as e:
            log_something_harvester("Harvester", "TYPE_ERROR", repr(e))

        if self._cycle_number % 5 == 0:
            self.update_configuration()
        if self._cycle_number > 1440:
            self._cycle_number = 0
            pass
        self._cycle_number +=1

    def stop(self):
        """
        Public method which allows to completely stop the harvester.
        It close the pool of process and stop the timer which periodically
        call the harvesting functions.
        """
        self.refresh.cancel()
        self.my_pool_of_processes.close()

    def start(self):
        """
        Public method which allows to start the Harvester.
        #FIXME: Don't restart the pool of processes !!
        """
        #FIXME: Don't restart the pool of processes !!
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()

    def __str__(self):
        return str(self._projects)
