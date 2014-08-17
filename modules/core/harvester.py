# coding=utf-8

from threading import Timer
from multiprocessing.pool import Pool
from importlib import import_module

from modules.utils.config import config
from modules.database.logging import log_something_harvester
from modules.database.boinc_mongo import get_all_project, clean_database_project


class Singleton(type):

    """
    Class which allows the creation of singleton,

    It is used to make Harvester as a singleton. It could be useful in the future, when we will add remote control
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
    Main class for harvesting.

    This class is the class which do all the harvesting part
    it will look into the database to find the different projects.
    And then run a process with the specified harvesting function and
    parameters specified in the database.

    We can have only one Harvester at the same time, that's why it is
    a singleton.
    """

    def __init__(self):
        projects_from_mongo = get_all_project()
        self._projects = {}
        self._cycle_number = 0
        for project in projects_from_mongo:
            if not "name" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR", "A project without name in database " +
                                        str(project._id) + ", skipped ...")
            else:
                self.add_project(project)
        self.interval = int(config["ASFBAH"]["REFRESH_RATE"])
        self.my_pool_of_processes = Pool(int(config["ASFBAH"]["CPU_CORE_TO_USE_FOR_HARVESTING"]))
        self.refresh = None
        self.check_state_timer()

    def update_configuration(self):
        """
        Update the configuration of projects.

        This function will look to see if a project has been added or deleted or modified, if it is the case
        it will automatically update the project list of the Harvester to take in count user modification.
        """
        projects_from_mongo = get_all_project()
        projects_name = list(self._projects)
        for project in projects_from_mongo:
            if not "name" in project:
                log_something_harvester("HARVESTER", "TYPE_ERROR", "A project without name in database "
                                        + str(project._id) + ", skipped ...")
            else:
                if not project["name"] in self._projects:
                    self.add_project(project)
                else:
                    self.update_project(project)
                    del projects_name[projects_name.index(project["name"])]

        for name in projects_name:
            del self._projects[name]


    def check_state_timer(self):
        """
        Update periodically the Harvester.

        This function is called everytime the timer of the Harvester tick. In this case the function will update
        the ETA of every project but also call if it is necessary the update of the projects or the cleaning of
        the database.

        :return: None
        """
        del self.refresh
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.refresh.start()
        try:
            for project_name in self._projects:
                project = self._projects[project_name]
                project["ETA"] -= self.interval
                if project["ETA"] <= 0:
                    project["ETA"] = int(project["frequency"])
                    parameters = ()
                    function_to_run = getattr(import_module("modules.core.harvesting_function"),
                                              project["harvesting_function"])
                    variables_for_process = function_to_run.__code__.co_varnames[:function_to_run.__code__.co_argcount]
                    for arg in variables_for_process:
                        parameters += (project[arg],)
                    parameters = ((parameters,))
                    self.my_pool_of_processes.starmap_async(function_to_run,
                                                            parameters)
            if self._cycle_number % 5 == 0:
                self.update_configuration()
            if self._cycle_number > 1440:
                for project in self._projects:
                    clean_database_project(project)
                self._cycle_number = 0
            self._cycle_number += 1
        except Exception as e:
            log_something_harvester("Harvester", "TYPE_ERROR", repr(e))

    def stop(self):
        """
        Public method which allows to completely stop the harvester.

        It close the pool of process and stop the timer which periodically
        call the harvesting functions.
        """
        self.refresh.cancel()
        self.refresh = None
        self.my_pool_of_processes.close()

    def start(self):
        """ Public method which allows to start the Harvester. """
        self.refresh = Timer(self.interval, self.check_state_timer)
        self.my_pool_of_processes = Pool(int(config["ASFBAH"]["CPU_CORE_TO_USE_FOR_HARVESTING"]))
        self.refresh.start()

    def add_project(self, project):
        """
        Add a project to the list of project to harvest by Harvester.

        This function will add to the harvester list of project to harvest the project passed in parameter.
        In case a critical parameter for the Harvester is missing (Things which shouldn't happen because the
        integrity of data ias checked on the front end part) default value will be assigned.

        :param project: The project that we want to add to the list of project to harvest.
        :return: None
        """
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
        self._projects[project["name"]] = project

    def update_project(self, project):
        """
        Update the project configuration of the project already in the harvester list.

        :param project: Project to update
        :return: None
        """
        current_project = self._projects[project["name"]]
        for field in project:
            if current_project[field] != project[field]:
                current_project = project[field]
