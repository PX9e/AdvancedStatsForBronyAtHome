from .mongodb_operations_low import db
from datetime import datetime


def log_something_harvester(module_name, type_of_error, message):
    log = {'module': module_name, 'type': type_of_error, 'message': message, 'datetime': datetime.now()}
    db["ASFBAH"]["logging"]["harvester"].insert(log)


def get_all_log_harvester(limit=-1, parameter_ajax=None):

    request = db["ASFBAH"]["logging"]["harvester"]
    if parameter_ajax:
        arguments = {}
        if parameter_ajax["datetime"]:
            arguments["datetime"] = {'$gt': datetime.strptime(parameter_ajax["datetime"], "%Y-%m-%d %H:%M:%S.%f")}
        if parameter_ajax["limit"]:
            limit = parameter_ajax["limit"]
        request = request.find(arguments)
    else:
        request = request.find({})

    if limit == -1:
        return request.sort("datetime", -1).limit(0)
    else:
        return request.sort("datetime", -1).limit(limit)

