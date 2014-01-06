from .mongodb_operations_low import db
from datetime import datetime


def log_something(module_name, type_of_error, message):
    log = {'module': module_name, 'type': type_of_error, 'message': message, 'datetime': datetime.now()}
    db["ASFBAH"]["logging"].insert(log)


def get_all_log():
    return db["ASFBAH"]["logging"].find({})