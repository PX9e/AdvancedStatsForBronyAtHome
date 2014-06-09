# coding=utf-8


from os import path
from time import time

from modules.boinc.stat_file_operation import (db_tables_data_extraction,
                                               db_dump_data_extraction,
                                               search_team_in_file_by_name_boinc,
                                               search_team_in_file_by_name_fah,
                                               search_users_in_file_by_id_boinc,
                                               search_hosts_in_file_by_ids_boinc,
                                               TeamStat)
from modules.database.boinc_mongo import (update_projects_harvest_time,
                                          register_stats_state_in_database)

from modules.database.logging import log_something_harvester, TypeLog
from modules.network.http_request_high_level import download_file
from modules.utils.config import config
from modules.utils.decompression import decompression
from modules.utils.exceptions import NoProjectException


def boinc_compute_extra_stats(Team):
    project_data = Team.attributs["project_data"]
    team_data = Team.attributs["team_data"]
    if "total_credit" in team_data and "total_credit" in project_data:
        team_data["total_credit_percent"] = float(
            team_data["total_credit"]) / float(project_data["total_credit"])

    if "members" in team_data and "nusers" in project_data:
        team_data["member_percent"] = team_data["members"]/project_data["nusers"]

    if "hosts" in team_data and "nhosts" in project_data:
        team_data["member_percent"] = team_data["hosts"]/project_data["nhosts"]

    Team.attributs["team_data"] = team_data
    return Team


def harvest_boinc_project(name, url, last_time_harvested):
    try:
        team_result = TeamStat()
        log_something_harvester(name, TypeLog.Start, "STARTING ... ")
        start = time()
        log_something_harvester(name, TypeLog.Info, "Downloading tables.xml...")
        table_xml = download_file(url + "tables.xml",
                                  config["ASFBAH"]["CFG_SHARED_TMP_PATH"]
                                  + name + path.sep + "tables.xml")
        log_something_harvester(name, TypeLog.Info, "Processing tables.xml...")
        info_table_xml = db_tables_data_extraction("", table_xml)

        if (not last_time_harvested) or (
                last_time_harvested and last_time_harvested <= info_table_xml[
                "last_update"]):
            del info_table_xml["last_update"]
            for project_data in info_table_xml:
                team_result["project_data"][project_data] = info_table_xml[
                    project_data]

            log_something_harvester(name, TypeLog.Info,
                                    "Downloading db_dump.xml ... ")
            dump_xml = download_file(url + "db_dump.xml",
                                     config["ASFBAH"]["CFG_SHARED_TMP_PATH"] +
                                     name + path.sep + "db_dump.xml")
            log_something_harvester(name, TypeLog.Info,
                                    "Processing db_dump.xml ... ")
            files_to_download = db_dump_data_extraction("", dump_xml)
            log_something_harvester(name, TypeLog.Info,
                                    "Downloading team file... ")
            file_to_extract = download_file(
                url + files_to_download["team"]["file"] + ".gz",
                config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
                "team.gz")
            log_something_harvester(name, TypeLog.Info, "Extracting ... ")
            file_pr = decompression(file_to_extract, False)
            log_something_harvester(name, TypeLog.Info,
                                    "Looking for " + config["ASFBAH"][
                                        "TEAM"] + " data ... ")
            try:
                team_result.attributs = search_team_in_file_by_name_boinc(
                    file_pr, config["ASFBAH"]["TEAM"])
            except NoProjectException:
                log_something_harvester(name, TypeLog.Info,
                                        "No Team " + config["ASFBAH"][
                                            "TEAM"] + " into data ... ")
                return None
            log_something_harvester(name, TypeLog.Info,
                                    "Downloading user file... ")
            file_to_extract = download_file(
                url + files_to_download["user"]["file"] + ".gz",
                config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
                "user.gz")
            log_something_harvester(name, TypeLog.Info, "Extracting ... ")
            file_pr = decompression(file_to_extract, False)
            log_something_harvester(name, TypeLog.Info,
                                    "Downloading host file... ")
            users = search_users_in_file_by_id_boinc(file_pr,team_result["id"])
            team_result.attributs["team_data"]["members"] = len(users)
            file_to_extract = download_file(
                url + files_to_download["host"]["file"] + ".gz",
                config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep +
                "host.gz")
            log_something_harvester(name, TypeLog.Info, "Extracting ... ")
            file_pr = decompression(file_to_extract, False)
            hosts = search_hosts_in_file_by_ids_boinc(file_pr, users)
            team_result.attributs["team_data"]["hosts"] = len(hosts)
            for project_data in info_table_xml:
                team_result.attributs["project_data"][project_data] = \
                    info_table_xml[project_data]
            team_result = boinc_compute_extra_stats(team_result)
            log_something_harvester(name, TypeLog.Info,
                                    "Injecting into database ... ")
            register_stats_state_in_database(team_result, name)
            update_projects_harvest_time(name)
            elapsed = (time() - start)
            log_something_harvester(name, TypeLog.Compelete, "Complete in " +
                                                             str(
                                                                 round(elapsed,
                                                                       3)) + " sec")
        else:
            log_something_harvester(name, TypeLog.Compelete,
                                    "Already up-to-date")
    except Exception as e:
        log_something_harvester(name, TypeLog.Error, repr(e))


def harvest_folding_at_home_project(name="Folding@Home"):
    team_result = TeamStat()
    try:
        log_something_harvester(name, TypeLog.Start, "STARTING ... ")
        start = time()
        log_something_harvester(name, TypeLog.Info,
                                "Downloading daily_team_summary.txt.bz2... ")
        file_to_extract = download_file(
            "http://fah-web.stanford.edu/daily_team_summary.txt.bz2",
            config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + str(path.sep) +
            "daily_team_summary.txt.bz2")
        log_something_harvester(name, TypeLog.Info, "Extracting ... ")
        file_pr = decompression(file_to_extract, False)
        log_something_harvester(name, TypeLog.Info,
                                "Looking for " + config["ASFBAH"][
                                    "TEAM"] + " data ... ")
        try:
            team = search_team_in_file_by_name_fah(file_pr,
                                                   config["ASFBAH"]["TEAM"])
        except NoProjectException:
            log_something_harvester(name, TypeLog.Info,
                                    "No Team " + config["ASFBAH"][
                                        "TEAM"] + " into data ... ")
            return None
        log_something_harvester(name, TypeLog.Info,
                                "Injecting into database ... ")
        register_stats_state_in_database(team, name)
        elapsed = (time() - start)
        log_something_harvester(name, TypeLog.Compelete, "Complete in " + str(
            round(elapsed, 3)) + " sec")

    except Exception as e:
        log_something_harvester(name, TypeLog.Error, repr(e))


list_functions = [
    ["harvest_boinc_project", ["representation", "url", "frequency"]],
    ["harvest_folding_at_home_project", ["representation", "frequency"]]]
