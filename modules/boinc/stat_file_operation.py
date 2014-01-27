import datetime


class ProjectConfiguration:
    def __init__(self, name=None, url=None, frequency=None, representation=None, last_time_harvested=None):
        if frequency:
            try:
                if not isinstance(frequency, int):
                    frequency = int(frequency)
            except Exception:
                frequency = None

        self.attributs = {"name": name, "url": url, "frequency": frequency, "representation": representation,
                          "last_time_harvested": last_time_harvested}

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
        self.attributs = {"id": None, "type": None, "name": None, "total_credit": None, "expavg_credit": None,
                          "expavg_time": None, "founder": None, "create_time": None, "description": None,
                          "country": None, "date": datetime.datetime.now()}

    def __str__(self):
        return str(self.attributs)

    def __repr__(self):
        return str(self.attributs)

    def __setitem__(self, key, value):
        self.attributs[key] = value

    def __getitem__(self, item):
        return self.attributs[item]

    def get_stats(self):
        return {"name": self.attributs["name"], "total_credit": self.attributs["total_credit"],
                "expavg_credit": self.attributs["expavg_credit"], "expavg_time": self.attributs["expavg_time"],
                "date": datetime.datetime.now()}


class TeamsResume:
    def __init__(self):
        self.list = {}

    def insert_team(self, team):
        self.list[team.attributs["name"]] = team

    def best_value(self, team, value):
        max_value = 0
        for team in self.list:
            if team.attributs[value] > max_value:
                max_value = team.attributs[value]

        return max_value


def search_team_in_file_by_name(file_path, name):
    file_to_read = open(file_path, "r")
    team_result = TeamStat()
    to_return = False
    storing = False

    a = file_to_read.read()
    a = a.split("\\n")

    for line in a:
        tag = fast_search_tag(line)
        if tag == "team":
            storing = True
        elif tag == "/team" and to_return:
            return team_result
        elif tag == "name":
            team_result[tag] = fast_search_value(line)
            if team_result[tag] == name:
                to_return = True
            else:
                storing = False
        elif storing:
            team_result[tag] = fast_search_value(line)
    raise Exception("Critical Error: EOF reaches without finding closing tag.")


def fast_search_tag(line):
    return line[line.find("<") + 1:line.find(">")]


def fast_search_value(line):
    """
    Doesn't search the tag,just get the value in the line for the tag.
    tag variable is here only to accelerate the process !
    """
    return line[line.find(">") + 1:  line.rfind("<")]


def db_dump_data_extraction(file_path, name):
    file_to_read = open(file_path + name)
    result = []
    record_table = {}
    for line in file_to_read.readlines():
        if line.find("<ta") > -1:
            if record_table:
                result.append(record_table)
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
        result.append(record_table)
    return result


def db_tables_data_extraction(file_path, name):
    file_to_read = open(file_path + name)
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
