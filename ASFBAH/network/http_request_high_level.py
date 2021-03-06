# coding=utf-8

from time import sleep
from urllib import request, error
from os.path import isfile
import os

from ASFBAH.utils.string_operation import (extract_file_type_from_url,
                                            try_to_extract_project_name_from_url
                                            )
from ASFBAH.utils.config import config


def download_file(url_of_file, path_to_write_file=None):
    """
    *Download a file*
    download_file is a function which will download a file and take two
    parameters, to be sure that this function
    work you need to be connected to internet...
    You have to manage exception when you can this function
    :param url_of_file: url of the file to download
    :type str
    :param path_to_write_file: where the function will create the file,
    you have to be sure that you have the rights
    to write there
    :type path_to_write_file: str
    :param url_of_file: where is the file to download
    :type str
    """
    connection = None
    nbtry = 1
    while nbtry < 4 and not connection:
        try:
            connection = request.urlopen(url_of_file)
        except error.URLError:
            print("Connection try %s failed" % nbtry)
            sleep(5)
            nbtry += 1

    if not connection:
        raise Exception("We failed to connect to the url %s" % url_of_file)
    data = connection.read()
    if path_to_write_file:
        try:
            file_to_write = open(path_to_write_file, 'wb')
        except:
            if not os.path.exists(os.path.dirname(path_to_write_file)):
                os.makedirs(os.path.dirname(path_to_write_file))
            file_to_write = open(path_to_write_file, 'wb')
        file_to_write.write(data)
        file_to_write.close()
    else:
        name_file = try_to_extract_project_name_from_url(
            url_of_file) + extract_file_type_from_url(url_of_file)
        path_to_write_file = config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name_file
        try:
            file_to_write = open(path_to_write_file, 'wb')
        except:
            if not os.path.exists(os.path.dirname(path_to_write_file)):
                os.makedirs(os.path.dirname(path_to_write_file))
            file_to_write = open(path_to_write_file, 'wb')
        file_to_write.write(data)
        file_to_write.close()
    if isfile(path_to_write_file):
        return path_to_write_file
    else:
        raise Exception()
