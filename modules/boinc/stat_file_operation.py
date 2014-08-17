# coding=utf-8

import time
from modules.utils.exceptions import NoProjectException


class ProjectConfiguration:
    def __init__(self, name=None, function_to_execute=None, frequency=None,
                 **kwargs):
        if frequency:
            try:
                if not isinstance(frequency, int):
                    frequency = int(frequency)
            except (ValueError, TypeError):
                frequency = 3600

        self.attributs = {"name": name, "frequency": frequency,
                          "harvesting_function": function_to_execute,
                          "category": None, "description": None,
                          "last_time_harvested": None}

        for keyword in kwargs:
            self.attributs[keyword] = kwargs[keyword]

    def __str__(self):
        return str(self.attributs)

    def __repr__(self):
        return str(self.attributs)

    def __setitem__(self, key, value):
        self.attributs[key] = value

    def __getitem__(self, item):
        return self.attributs[item]


class TeamStat:
    def __init__(self):
        self.attributs = {"project_type": None,
                          "name": None, "date": time.time(),
                          "team_data": {},
                          "project_data": {}
        }

    def __str__(self):
        return str(self.attributs)

    def __repr__(self):
        return str(self.attributs)

    def __setitem__(self, key, value):
        self.attributs[key] = value

    def __getitem__(self, item):
        return self.attributs[item]

    def get_stats(self):
        return self.attributs


def search_team_in_file_by_name_fah(file_path, name):
    file_to_read = open(file_path, "rb")
    team_result = TeamStat()
    pattern = "\t" + name + "\t"
    index_before_read = 0
    index_after_read = -1
    while index_after_read != index_before_read:
        index_before_read = file_to_read.tell()
        line = file_to_read.readline()
        oper = line.decode('latin1')
        if oper.find(pattern) > -1:
            the_line = oper.strip("\n")
            the_data = the_line.split("\t")
            team_result["id"] = the_data[0]
            team_result["name"] = the_data[1]
            team_result["team_data"]["total_credit"] = the_data[2]
            team_result["project_data"]["wu"] = the_data[3]
            team_result["project_type"] = "fah"
            return team_result
        index_after_read = file_to_read.tell()
    raise NoProjectException(
        "Critical Error: EOF reaches without finding the team")


def search_users_in_file_by_id_boinc(file_path, teamid):
    file_to_read = open(file_path)
    storing = False
    users = {}
    temp_user = {}
    index_before_read = 0
    index_after_read = -1
    while index_after_read != index_before_read:
        index_before_read = file_to_read.tell()
        line = file_to_read.readline()
        tag = fast_search_tag(line)
        if tag == "user":
            storing = True
        elif tag == "/user":
            storing = False
        elif tag == "teamid":
            if str(fast_search_value(line)) == str(teamid):
                users[temp_user["id"]] = temp_user["name"]
        elif storing:
            if tag == "name":
                temp_user["name"] = fast_search_value(line)
            elif tag == "id":
                temp_user["id"] = fast_search_value(line)

        index_after_read = file_to_read.tell()
    return users


def search_hosts_in_file_by_ids_boinc(file_path, usersid):
    file_to_read = open(file_path)
    storing = False
    confirm = False
    hosts = {}
    temp_host = {}
    index_before_read = 0
    index_after_read = -1
    while index_after_read != index_before_read:
        ind_before_read = file_to_read.tell()
        line = file_to_read.readline()
        tag = fast_search_tag(line)
        if tag == "host":
            storing = True
        elif tag == "/host":
            if confirm and storing:
                hosts[temp_host["rpc_time"]] = temp_host["fpops"]
            storing = False
        elif tag == "userid":
            if str(fast_search_value(line)) in usersid:
                confirm = True
            else:
                confirm = False
        elif storing:
            if tag == "p_fpops":
                temp_host["fpops"] = fast_search_value(line)
            elif tag == "rpc_time":
                temp_host["rpc_time"] = fast_search_value(line)
        index_after_read = file_to_read.tell()

    return hosts


def search_team_in_file_by_name_boinc(file_path, name, team_stats):
    from copy import deepcopy
    team_data_to_extract = ["total_credit", "expavg_credit", "expavg_time"]
    project_data_to_extract = []
    global_data_to_extract = ["name", "id"]
    file_to_read = open(file_path)
    temp_team = TeamStat().attributs
    result_team = {}
    to_return = False
    storing = False
    index_before_read = 0
    index_after_read = -1
    teamscores = []
    while index_after_read != index_before_read:
        index_before_read = file_to_read.tell()
        line = file_to_read.readline()
        tag = fast_search_tag(line)
        if tag == "team":
            storing = True
        elif tag == "/team":
            if to_return:
                temp_team["project_type"] = "boinc"
                result_team = deepcopy(temp_team)
            teamscores.append(temp_team["team_data"]["total_credit"])
            storing = False
            to_return = False
        elif tag == "name":
            temp_team[tag] = fast_search_value(line)
            if temp_team[tag] == name:
                to_return = True
        elif storing:
            if tag in team_data_to_extract:
                try:
                    temp_team["team_data"][tag] = float(fast_search_value(line))
                except ValueError:
                    temp_team["team_data"][tag] = fast_search_value(line)
            elif tag in project_data_to_extract:
                try:
                    temp_team["project_data"][tag] = float(fast_search_value(line))
                except ValueError:
                    temp_team["project_data"][tag] = fast_search_value(line)
            elif tag in global_data_to_extract:
                try:
                    temp_team[tag] = float(fast_search_value(line))
                except ValueError:
                    temp_team[tag] = fast_search_value(line)

        index_after_read = file_to_read.tell()

    teamscores = sorted(teamscores, reverse=True)
    team_stats["team_data"]["position"] = teamscores.index(
        result_team["team_data"]["total_credit"]) + 1
    team_stats.update(result_team)
    if result_team:
        return result_team
    else:
        raise NoProjectException("Critical Error: EOF reaches without finding the team")


def fast_search_tag(line):
    return line[line.find("<") + 1:line.find(">")]


def fast_search_value(line):
    """Doesn't search the tag,just get the value in the line."""
    return line[line.find(">") + 1:  line.rfind("<")]


def db_dump_data_extraction(file_path, name):
    #We open the downloaded file
    file_to_read = open(file_path + name)

    result = {}

    record_table = {}

    for line in file_to_read.readlines():
        if line.find("<ta") > -1:
            if record_table:
                result[record_table["name"]] = record_table
                record_table = {}
            name_table = fast_search_value(line)
            record_table["name"] = name_table
        elif line.find("<fil") > -1:
            name_file = fast_search_value(line)
            record_table["file"] = name_file
        elif line.find("<co") > -1:
            compression = fast_search_value(line)
            record_table["compression"] = compression
    if record_table:
        result[record_table["name"]] = record_table
    return result


def db_tables_data_extraction(file):
    file_to_read = open(file)
    record_table = {}
    for line in file_to_read.readlines():
        if line.find("<update_time>") > -1:
            value = fast_search_value(line)
            record_table["last_update"] = int(value)
        elif line.find("<nusers") > -1:
            value = fast_search_value(line)
            record_table["nusers"] = value
        elif line.find("<nteams") > -1:
            value = fast_search_value(line)
            record_table["nteams"] = value
        elif line.find("<nhosts") > -1:
            value = fast_search_value(line)
            record_table["nhosts"] = value
        elif line.find("<total") > -1:
            value = fast_search_value(line)
            record_table["total_credit"] = value
            break
    return record_table
