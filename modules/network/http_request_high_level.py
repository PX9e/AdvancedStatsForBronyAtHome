#
#
#
#

from urllib2 import urlopen
from os.path import isfile


def download_file(path_to_write_file, url_of_file):
    """
    Download a file
    @download_file is a function which will download a file and take two parameters, to be sure that this function
    work you need to be connected to internet...
    You have to manage exception when you can this function
    @path_to_write_file:string where the function will create the file, you have to be sure that you have the rights
    to write there
    @url_of_file where:string where is the file to download
    """

    connection = urlopen(url_of_file)
    data = connection.read()

    file_to_write = open(path_to_write_file, 'w')
    file_to_write.write(data)
    file_to_write.close()

    if isfile(path_to_write_file):
        return True
    else:
        return False

