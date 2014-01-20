from .mongodb_operations_low import db
from datetime import datetime
import re


def log_something_harvester(module_name, type_of_error, message):
    log = {'module': module_name, 'type': type_of_error, 'message': message, 'datetime': datetime.now()}
    db["ASFBAH"]["logging"]["harvester"].insert(log)


def get_all_log_harvester(limit=-1, parameter_ajax=None):
    order = -1
    print(str(parameter_ajax))
    request = db["ASFBAH"]["logging"]["harvester"]
    if parameter_ajax:
        arguments = {}
        if "datetime" in parameter_ajax:
            if parameter_ajax["datetime"] != "":
                arguments["datetime"] = {'$gt': datetime.strptime(parameter_ajax["datetime"], "%Y-%m-%d %H:%M:%S.%f")}

        if "limit" in parameter_ajax:
            limit = int(parameter_ajax["limit"])
        if "order" in parameter_ajax:
            order = int(parameter_ajax["limit"])
        if "type" in parameter_ajax:
            arguments["type"] = {'$in': parameter_ajax.getlist("type")}
        if "module" in parameter_ajax:
            if parameter_ajax["module"] != "":
                import re
                regx = re.compile("^" + parameter_ajax["module"] + ".*", re.IGNORECASE)

                arguments["module"] = regx
        request = request.find(arguments)
    else:
        request = request.find({})

    if limit == -1:
        return request.sort("datetime", order).limit(0)
    else:
        return request.sort("datetime", order).limit(limit)

