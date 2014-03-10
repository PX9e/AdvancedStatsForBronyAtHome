from datetime import datetime
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
    project_configuration_to_save.attributs["date_update"] = time.time()
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
        updates["date_update"] = time.time()
        db["ASFBAH"]["project_list"].update(keys, {'$set': updates})


def remove_a_project(id_project):
    if id_project:
        if not isinstance(id_project, ObjectId):
            id_project = ObjectId(id_project)
        db["ASFBAH"]["project_list"].remove({'_id': id_project})


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


def get_server_date():
        return {"date": time.time()}



def get_all_project():
    return db["ASFBAH"]["project_list"].find({})


def get_all_project_by_date(date=None):
    if not date or date == 0:
        return get_all_project()
    return db["ASFBAH"]["project_list"].find({'$gt': float(date)})


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
