from os import path
from time import time

from modules.boinc.stat_file_operation import (db_tables_data_extraction,
                                               db_dump_data_extraction,
                                               search_team_in_file_by_name_boinc,
                                               search_team_in_file_by_name_fah)
from modules.database.boinc_mongo import (update_projects_harvest_time,
                                          register_stats_state_in_database)
from modules.database.logging import log_something_harvester
from modules.network.http_request_high_level import download_file
from modules.utils.config import config
from modules.utils.decompression import decompression
from modules.utils.exceptions import NoProjectException


def harvest_boinc_project(name, url, last_time_harvested):
    try:
        log_something_harvester(name, "TYPE_START", "STARTING ... ")
        start = time()
        log_something_harvester(name, "TYPE_INFO", "Downloading tables.xml... ")
        #table_xml = download_file(url + "tables.xml", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
        #                                              "tables.xml")
        log_something_harvester(name, "TYPE_INFO", "Processing tables.xml... ")
        #info_table_xml = db_tables_data_extraction("", table_xml)
        if True:
        #if (last_time_harvested and last_time_harvested < info_table_xml["last_update"]) or (not last_time_harvested):
            log_something_harvester(name, "TYPE_INFO", "Downloading db_dump.xml ... ")
        #    dump_xml = download_file(url + "db_dump.xml", config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
        #                                                  "db_dump.xml")
            log_something_harvester(name, "TYPE_INFO", "Processing db_dump.xml ... ")
        #    files_to_download = db_dump_data_extraction("", dump_xml)
            log_something_harvester(name, "TYPE_INFO", "Downloading team file... ")
        #    file_to_extract = download_file(url + files_to_download["team"]["file"] + ".gz",
        #                                    config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
        #                                    "team.gz")
            log_something_harvester(name, "TYPE_INFO", "Extracting ... ")
        #    file_pr = decompression(file_to_extract, False)
            log_something_harvester(name, "TYPE_INFO", "Looking for " + config["ASFBAH"]["TEAM"] + " data ... ")
        #    try:
        #        team = search_team_in_file_by_name_boinc(file_pr, config["ASFBAH"]["TEAM"])
        #    except NoProjectException:
        #        log_something_harvester(name, "TYPE_INFO", "No Team " + config["ASFBAH"]["TEAM"] + " into data ... ")
        #        return None
            log_something_harvester(name, "TYPE_INFO", "Injecting into database ... ")
        #    register_stats_state_in_database(team, name)
        #    update_projects_harvest_time(name)
            elapsed = (time() - start)
            log_something_harvester(name, "TYPE_COMPLETE", "Complete in " + str(round(elapsed, 3)) + " sec")
        else:
            log_something_harvester(name, "TYPE_COMPLETE", "Already up-to-date")
    except Exception as e:
        log_something_harvester(name, "TYPE_ERROR", repr(e))


def harvest_folding_at_home_project(name="Folding@Home"):
    try:
        log_something_harvester(name, "TYPE_START", "STARTING ... ")
        start = time()
        log_something_harvester(name, "TYPE_INFO", "Downloading daily_team_summary.txt.bz2... ")
        file_to_extract = download_file("http://fah-web.stanford.edu/daily_team_summary.txt.bz2",
                                        config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + str(path.sep) +
                                        "daily_team_summary.txt.bz2")
        log_something_harvester(name, "TYPE_INFO", "Extracting ... ")
        file_pr = decompression(file_to_extract, False)
        log_something_harvester(name, "TYPE_INFO", "Looking for " + config["ASFBAH"]["TEAM"] + " data ... ")
        try:
            team = search_team_in_file_by_name_fah(file_pr, config["ASFBAH"]["TEAM"])
        except NoProjectException:
            log_something_harvester(name, "TYPE_INFO", "No Team " + config["ASFBAH"]["TEAM"] + " into data ... ")
            return None
        log_something_harvester(name, "TYPE_INFO", "Injecting into database ... ")
        register_stats_state_in_database(team, name)
        elapsed = (time() - start)
        log_something_harvester(name, "TYPE_COMPLETE", "Complete in " + str(round(elapsed, 3)) + " sec")

    except Exception as e:
        log_something_harvester(name, "TYPE_ERROR", repr(e))


list_functions = [["harvest_boinc_project", ["representation", "url", "frequency"]],
                  ["harvest_folding_at_home_project", ["representation", "frequency"]]]
