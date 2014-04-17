# coding=utf-8

def extract_file_name_from_url(url):
    return url[url.rfind("/") + 1:]


def extract_file_type_from_url(url):
    return url[url.rfind("."):]


def try_to_extract_project_name_from_url(url):
    url_without_protocol = url[url.find("//") + 2:]
    url_without_end = url_without_protocol[:url_without_protocol.find("/")]
    return url_without_end[
           url_without_end.find(".") + 1:url_without_end.rfind(".")]

