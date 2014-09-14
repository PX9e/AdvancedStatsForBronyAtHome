# coding=utf-8

import configparser
import os

realpath = os.path.realpath(__file__)
realpath = realpath[:realpath.rfind(os.sep)]


config = configparser.ConfigParser()
try:
    config.read(realpath + os.sep + "asfbah-local.config")
except:
    config.read(realpath + os.sep + "asfbah.config")


def generate_secret_key(length):
    import random

    secret_key = ""
    for i in range(0, length):
        val = random.randint(0, 61)
        if val < 26:
            secret_key += chr(val + 65)
        elif val > 51:
            secret_key += chr(val - 4)
        else:
            secret_key += chr(val + 71)

    return secret_key
