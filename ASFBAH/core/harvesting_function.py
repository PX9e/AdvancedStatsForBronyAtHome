# coding=utf-8

from os import path
from time import time

from ASFBAH.boinc.stat_file_operation import (db_tables_data_extraction,
                                              db_dump_data_extraction,
                                              search_team_in_file_by_name_boinc,
                                              search_team_in_file_by_name_fah,
                                              search_users_in_file_by_id_boinc,
                                              search_hosts_in_file_by_ids_boinc,
                                              TeamStat)
from ASFBAH.database.boinc_mongo import (update_projects_harvest_time,
                                         register_stats_state_in_database)
from ASFBAH.database.logging import log_something_harvester, TypeLog
from ASFBAH.network.http_request_high_level import download_file
from ASFBAH.utils.config import config
from ASFBAH.utils.decompression import decompression
from ASFBAH.utils.exceptions import NoProjectException


def boinc_compute_extra_stats(Team):
    """Compute some extra stats from basic ones.

    This function will compute some stats from basic ones.
    At the moment the function is computing the percentage of credits,
    of members and hosts of the team in the project.

    It is also cumputing the percentage of teams behind the team
    for which the harvester is working.

    :param Team, represent the complete set of stats for the team.
    :type Team: TeamStat Object

    :return Team with extra attributes
    """

    project_data = Team.attributs["project_data"]
    team_data = Team.attributs["team_data"]

    if "total_credit" in team_data and "total_credit" in project_data:
        team_data["total_credit_percent"] = float(
            team_data["total_credit"]) / float(project_data["total_credit"])

    if "members" in team_data and "nusers" in project_data:
        team_data["member_percent"] = float(team_data["members"]) / float(
            project_data["nusers"])

    if "hosts" in team_data and "nhosts" in project_data:
        team_data["hosts_percent"] = float(team_data["hosts"]) / float(
            project_data["nhosts"])

    if "positions" in team_data and "total_teams" in project_data:
        team_data["superiority"] = (float(project_data["total_teams"]) - float(
            team_data["positions"])) / float(
            project_data["total_teams"])

    Team.attributs["team_data"] = team_data
    return Team


def harvest_boinc_project(name, url, last_time_harvested):
    """
    Harvest and compute stats for the Boinc project 'name'.

    This function harvests and computes stats for the project with
    the name passed in parameter.

    This functions is 'smart' and will harvest only if necessary.
    Everything is logged into the database for further investigation.

    In normal time this function is called by the harvester in several
    different process disconnected from the harvester itself.

    :param name: Name of the project to harvest.
    :type  name: str
    :param url: Url of the project platform for harvesting.
    :type url: str
    :param last_time_harvested: Timestamp
    :type last_time_harvested: float

    :return: Nothing.
    """
    try:
        # Code factorization variable
        temp_path = config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + path.sep
        team = config["ASFBAH"]["TEAM"]
        start = time()

        # team_result is the TeamStat Object that will contain all the stats about the project.
        team_result = TeamStat()
        log_something_harvester(name, "STARTING...", TypeLog.Start)

        log_something_harvester(name, "Downloading tables.xml...")
        table_xml = download_file(url + "tables.xml", temp_path + "tables.xml")
        log_something_harvester(name, "Processing tables.xml...")
        info_table_xml = db_tables_data_extraction(table_xml)

        # We check that we should harvest or not, we harvest if we have never harvest the project of if the last time
        # we harvested it is inferior(Timestamp) to the
        if (not last_time_harvested) or (float(last_time_harvested + 1) < float(info_table_xml["last_update"])):
            del info_table_xml["last_update"]
            # Inject interesting data for statistics about the project.
            for project_data in info_table_xml:
                team_result["project_data"][project_data] = info_table_xml

            # The next block gets the names of files containing interesting data about the project.
            log_something_harvester(name, "Downloading db_dump.xml...")
            dump_xml = download_file(url + "db_dump.xml", temp_path + "db_dump.xml")
            log_something_harvester(name, "Processing db_dump.xml...")
            files_to_download = db_dump_data_extraction("", dump_xml)

            # The next block gets data about the team itself.
            log_something_harvester(name, "Downloading team file... ")
            file_to_extract = download_file(url + files_to_download["team"]["file"] + ".gz", temp_path + "team.gz")
            log_something_harvester(name, "Extracting...", TypeLog.Info)
            file_pr = decompression(file_to_extract)
            log_something_harvester(name, "Looking for {0} data...".format(team))
            try:
                search_team_in_file_by_name_boinc(file_pr, team, team_result)
            except NoProjectException:
                # The stat file doesn't contain any team with the name passed in parameter. We interrupt the harvest process
                log_something_harvester(name, "No Team {0} into data ... ".format(team),
                                        TypeLog.Info)
                return None

            log_something_harvester(name, "Downloading user file...")
            file_to_extract = download_file(
                url + files_to_download["user"]["file"] + ".gz", temp_path + 'user.gz')
            log_something_harvester(name, "Extracting...")
            file_pr = decompression(file_to_extract)
            users = search_users_in_file_by_id_boinc(file_pr, team_result["id"])
            team_result.attributs["team_data"]["members"] = len(users)

            log_something_harvester(name, "Downloading host file...")
            file_to_extract = download_file(
                url + files_to_download['host']['file'] + '.gz', temp_path + 'host.gz')
            log_something_harvester(name, "Extracting...")
            file_pr = decompression(file_to_extract)
            hosts = search_hosts_in_file_by_ids_boinc(file_pr, users)

            team_result.attributs["team_data"]["hosts"] = len(hosts)
            team_result = boinc_compute_extra_stats(team_result)

            log_something_harvester(name, "Injecting into database...")
            register_stats_state_in_database(team_result, name)
            update_projects_harvest_time(name)
            elapsed = (time() - start)
            log_something_harvester(name, "Complete in {0} sec".format(round(elapsed, 3)),
                                    TypeLog.Complete)
        else:
            log_something_harvester(name, "Already up-to-date", TypeLog.Complete)
    except Exception as e:
        # Unexpected error, no way to save the process, we log the error message
        log_something_harvester(name, repr(e), TypeLog.Error)


def harvest_folding_at_home_project(name="Folding@Home"):
    try:
        team = config["ASFBAH"]["TEAM"]
        log_something_harvester(name, "STARTING...", TypeLog.Start)
        start = time()
        log_something_harvester(name, "Downloading daily_team_summary.txt.bz2...")
        file_to_extract = download_file(
            "http://fah-web.stanford.edu/daily_team_summary.txt.bz2",
            config["ASFBAH"]["CFG_SHARED_TMP_PATH"] + name + str(
                path.sep) + "daily_team_summary.txt.bz2")
        log_something_harvester(name, "Extracting...", TypeLog.Info)
        file_pr = decompression(file_to_extract, False)
        log_something_harvester(name, "Looking for {0} data...".format(team))
        try:
            team = search_team_in_file_by_name_fah(file_pr, team)
        except NoProjectException:
            log_something_harvester(name, "No Team {0} into data...".format(team))
            return None
        log_something_harvester(name, "Injecting into database ... ")
        register_stats_state_in_database(team, name)
        elapsed = (time() - start)
        log_something_harvester(name, "Complete in {0} sec".format(round(elapsed, 3)),
                                TypeLog.Complete)
    except Exception as e:
        log_something_harvester(name, repr(e), TypeLog.Error)


list_functions = [
    ["harvest_boinc_project",
     ["representation", "url", "frequency", "category", "description"]],
    ["harvest_folding_at_home_project",
     ["representation", "frequency", "category", "description"]]]
