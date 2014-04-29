# coding=utf-8

__author__ = 'guillaume'

import time

class user(object):
    """
    Class wrapping the dict return by mongoDB, for flask-login session
    """

    def __init__(self, user_dict):
        self._user_param = user_dict


    def get_id(self):
        return self._user_param["session_id"]

    def is_active(self):
        print(str(self._user_param))
        if time.time() - 3600 > int(self._user_param["session_id_time"]):
            return False
        else:
            return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True