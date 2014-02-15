from modules.database.mongodb_operations_low import db
from pymongo.son_manipulator import ObjectId

import time


def register_stats_state_in_database(team_state_to_insert, project_name):
    db["ASFBAH"]["project_stats"][project_name]["stats"].insert(team_state_to_insert.get_stats())


def register_team_state_in_database(team_state_to_insert, project_name):
    db["ASFBAH"]["project_stats"][project_name]["teams"].insert(team_state_to_insert.attributs)


def get_collection(project_name):
    return db["ASFBAH"]["project_stats"][project_name]["stats"].find({})


def register_a_project(project_configuration_to_save):
    db["ASFBAH"]["project_list"].insert(project_configuration_to_save.attributs)


def update_a_project(keys, updates):
    if not (isinstance(keys, dict) and isinstance(updates, dict)):
        raise Exception("keys or udpates not a dict")
    else:
        if "_id" in keys:
            if not isinstance(keys['_id'], ObjectId):
                keys['_id'] = ObjectId(keys['_id'])
        if "_id" in updates:
            if not isinstance(updates['_id'], ObjectId):
                updates['_id'] = ObjectId(updates['_id'])

        db["ASFBAH"]["project_list"].update(keys, {'$set': updates})


def remove_a_project(id):
    if id:
        if not isinstance(id, ObjectId):
            id = ObjectId(id)
        db["ASFBAH"]["project_list"].remove({'_id': id})


def get_projects_custom(arguments=None, **kwargs):
    from pymongo.son_manipulator import ObjectId

    processed_arguments = {}

    if arguments:
        if not isinstance(arguments, dict):
            return None
        else:
            if "_id" in arguments:
                if not isinstance(arguments["_id"], ObjectId):
                    arguments["_id"] = ObjectId(arguments["_id"])
            processed_arguments = arguments

    for arg in kwargs:
        if arg == '_id':
            if not isinstance(kwargs[arg], ObjectId):
                kwargs[arg] = ObjectId(kwargs[arg])
        processed_arguments[arg] = kwargs[arg]

    return db["ASFBAH"]["project_list"].find(processed_arguments)


def get_all_project():
    return db["ASFBAH"]["project_list"].find({})


def update_projects_harvest_time(name):
    db["ASFBAH"]["project_list"].update({"name": name}, {"$set": {"last_time_harvested": time.time()}})


def get_projects_precise(name=None, url=None, representation=None, frequency=None, frequency_parameter="$gte"):
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


