# coding=utf-8
from modules.boinc.stat_file_operation import TeamStat
from modules.database.mongodb_operations_low import db
from pymongo.son_manipulator import ObjectId
from modules.utils.config import config
import uuid
import time


def register_stats_state_in_database(team_state_to_insert, project_name):
    return db["ASFBAH"]["project_stats"][project_name]["stats"].insert(
        team_state_to_insert.get_stats())


def register_team_state_in_database(team_state_to_insert, project_name):
    return db["ASFBAH"]["project_stats"][project_name]["teams"].insert(
        team_state_to_insert.attributs)


def clean_database_project(project_name):
    seventy_hours_in_sec = 259100
    twenty_four_hours_in_sec = 86400

    current_time = time.time()

    data_points = db["ASFBAH"]["project_stats"][project_name]["stats"].find({})
    data_points_to_process = []

    for data_point in data_points:
        if not data_point["date"] > current_time - seventy_hours_in_sec:
            data_points_to_process.append(data_point)

    data_points_to_process_sorted = sorted(data_points_to_process, key=lambda x: x["date"])


    prima_date = 0-seventy_hours_in_sec - 1

    for data_point in data_points_to_process_sorted:
        if data_point["date"] - twenty_four_hours_in_sec < prima_date:
            db["ASFBAH"]["project_stats"][project_name]["stats"].remove({'_id': data_point['_id']})
        else:
            prima_date = data_point["date"]


def get_collection(project_name):
    final_result = []
    for i in db["ASFBAH"]["project_stats"][project_name]["stats"].find({}):
        temp = i
        del temp['_id']
        final_result.append(temp)
    return final_result


def register_a_project(project_configuration_to_save):
    project_configuration_to_save.attributs["date_update"] = time.time()
    return db["ASFBAH"]["project_list"].insert(
        project_configuration_to_save.attributs)


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
        project = db["ASFBAH"]["project_list"].find(keys)
        keys_logging = {"module": project[0]["name"]}
        try:
            db["ASFBAH"]["project_stats"][project[0]["name"]]. \
                rename("project_stats." + updates["name"])
        except Exception as e:
            pass
        db["ASFBAH"]["logging"]["harvester"].update(
            keys_logging, {'$set': {"module": updates["name"]}}, multi=True)
        return db["ASFBAH"]["project_list"].update(keys, {'$set': updates})


def remove_a_project(id_project):
    if id_project:
        if not isinstance(id_project, ObjectId):
            id_project = ObjectId(id_project)
        project = db["ASFBAH"]["project_list"].find({'_id': id_project})
        db["ASFBAH"]["project_stats"][id_project].drop()
        db["ASFBAH"]["logging"]["harvester"].remove(
            {'module': project[0]["name"]})
        return db["ASFBAH"]["project_list"].remove({'_id': id_project})

    return None


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


def get_list_all_project():
    my_list_result = []
    projects = db["ASFBAH"]["project_list"].find({})
    for project in projects:
        my_list_result.append(project)
    return my_list_result


def get_list_all_user():
    return None


def get_all_project_by_date(date=None):
    if not date or date == 0:
        return get_all_project()
    return db["ASFBAH"]["project_list"].find({'$gt': float(date)})


def update_projects_harvest_time(name):
    return db["ASFBAH"]["project_list"].update({"name": name}, {
        "$set": {"last_time_harvested": time.time()}})


def get_projects_precise(name=None, url=None, representation=None,
                         frequency=None, frequency_parameter="$gte"):
    request_parameter = {}
    if name:
        request_parameter["name"] = {name}
    if url:
        request_parameter["url"] = {url}
    if frequency:
        if not isinstance(frequency, int):
            request_parameter["frequency"] = {
                frequency_parameter: int(frequency)}
    if representation:
        request_parameter["representation"] = {representation}
    return db["ASFBAH"]["project_list"].find(request_parameter)


def get_user(name):
    user = db["ASFBAH"]["USERS"].find({"name": name})
    if user.count() > 0:
        return user[0]
    else:
        return None


def identification(name, password):
    import crypt

    user = get_user(name)
    if user:
        if crypt.crypt(password, "$6$" + config["ASFBAH"]["SECRET_KEY"]) == \
                user["password"]:
            return True
        else:
            return False
    else:
        return False


def add_user(name, password):
    import crypt

    if not get_user(name):
        user = {"name": name, "password": crypt.crypt(password,
                                                      "$6$" + config["ASFBAH"][
                                                          "SECRET_KEY"])}
        db["ASFBAH"]["USERS"].insert(user)
        return True
    else:
        return False


def add_user_session_uuid(username):
    my_user = get_user(username)
    if my_user:
        if "session_id" in my_user:
            if time.time() - 3600 > int(my_user["session_id_time"]):
                session_id = uuid.uuid4()
                db["ASFBAH"]["USERS"].update({"name": username}, {
                    "$set": {"session_id": str(session_id)}})
                db["ASFBAH"]["USERS"].update({"name": username}, {
                    "$set": {"session_id_time": time.time()}})
                my_user = get_user(username)
                return my_user
            else:
                return my_user
        else:
            session_id = uuid.uuid4()
            db["ASFBAH"]["USERS"].update({"name": username}, {
                "$set": {"session_id": str(session_id)}})
            db["ASFBAH"]["USERS"].update({"name": username}, {
                "$set": {"session_id_time": time.time()}})
            my_user = get_user(username)
            return my_user
    else:
        return None
