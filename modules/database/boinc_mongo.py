from .mongodb_operations_low import db
import time


def register_stats_state_in_database(team_state_to_insert, project_name):
    db["ASFBAH"]["project_stats"][project_name]["stats"].insert(team_state_to_insert.get_stats())


def register_team_state_in_database(team_state_to_insert, project_name):
    db["ASFBAH"]["project_stats"][project_name]["teams"].insert(team_state_to_insert.attributs)


def get_collection(project_name):
    return db["ASFBAH"]["project_stats"][project_name]["stats"].find({})


def register_a_project(project_configuration_to_save):
    db["ASFBAH"]["project_list"].insert(project_configuration_to_save.attributs)


def get_all_project():
    return db["ASFBAH"]["project_list"].find({})


def update_projects_harvest_time(name):
    db["ASFBAH"]["project_list"].update({"name": name}, {"$set": {"last_time_harvested": time.time()}})


def get_projects(name=None, url=None, representation=None, frequency=None, frequency_parameter="$gte"):
    request_parameter = {}
    if name:
        request_parameter["name"] = {name}
    if url:
        request_parameter["url"] = {url}
    if frequency:
        if not isinstance(frequency, int):
            request_parameter["frequency"] = {frequency_parameter: int(frequency)}
    if representation:
        request_parameter["representation"] = {representation}
    return db["ASFBAH"]["project_list"].find(request_parameter)


def ajax_project_operation_backend(ajax_parameter):
    if "operation" in ajax_parameter:
        if ajax_parameter["operation"] == "modification":
            return True
        elif ajax_parameter["operation"] == "insertion":
            return True
        elif ajax_parameter["operation"] == "deletion":
            return True
        else:
            return False
    else:
        return False


