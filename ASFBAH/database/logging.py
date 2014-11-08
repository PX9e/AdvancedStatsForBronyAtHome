# coding=utf-8


import re
import time

from .mongodb_operations_low import db


def log_something_harvester(module_name, type_of_message, message):
    """
    Log message in the database.

    This function will log message in the database with the type of message passed in parameter.
    This allow asynchronous communication between process and fast sortable retrival of log
    messages.

    :param module_name: Name of the module sending the message
    :type module_name: str
    :param type_of_message: Type of the message by default it can be anything but for standardization
    you should use one of the value in the class TypeLog.
    :type type_of_message: str
    :param message: Message to save in the database.
    :type message: str
    """
    log = {'module': module_name, 'type': type_of_message, 'message': message,
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
        if "type[]" in parameter_ajax:
            arguments["type"] = {'$in': parameter_ajax.getlist("type[]")}
        if "module" in parameter_ajax:
            if parameter_ajax["module"] != "":
                regx = re.compile("^" + parameter_ajax["module"] + ".*",
                                  re.IGNORECASE)
                arguments["module"] = regx

        request = request.find(arguments)
    else:
        request = request.find({})

    if limit == -1:
        return request.sort("datetime", order).limit(0)
    else:
        return request.sort("datetime", order).limit(limit)


class TypeLog():

    """Define regular type of log message"""

    Error = "TYPE_ERROR"
    Info = "TYPE_INFO"
    Start = "TYPE_START"
    Complete = "TYPE_COMPLETE"