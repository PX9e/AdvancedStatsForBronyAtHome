# coding=utf-8


from .mongodb_operations_low import db

import re
import time


def log_something_harvester(module_name, type_of_error, message):
    log = {'module': module_name, 'type': type_of_error, 'message': message,
           'datetime': time.time()}
    db["ASFBAH"]["logging"]["harvester"].insert(log)


def get_all_log_harvester(limit=-1, parameter_ajax=None):
    order = -1
    request = db["ASFBAH"]["logging"]["harvester"]
    if parameter_ajax:
        arguments = {}
        if "datetime" in parameter_ajax:
            if parameter_ajax["datetime"] != "":
                arguments["datetime"] = {
                    '$gt': float(parameter_ajax["datetime"])}

        if "limit" in parameter_ajax:
            limit = int(parameter_ajax["limit"])
        if "order" in parameter_ajax:
            order = int(parameter_ajax["limit"])
        if "type" in parameter_ajax:
            arguments["type"] = {'$in': parameter_ajax.getlist("type")}
        if "module" in parameter_ajax:
            if parameter_ajax["module"] != "":
                regx = re.compile("^" + parameter_ajax["module"] + ".*",
                                  re.IGNORECASE)
                arguments["module"] = regx
        print(arguments)
        request = request.find(arguments)
    else:
        request = request.find({})

    if limit == -1:
        return request.sort("datetime", order).limit(0)
    else:
        return request.sort("datetime", order).limit(limit)


class TypeLog():
    Error = "TYPE_ERROR"
    Info = "TYPE_INFO"
    Start = "TYPE_START"
    Compelete = "TYPE_COMPLETE"