import datetime


class Team:

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

    def insert_team(self,team):
        self.list[team.attributs["name"]] = team

    def best_value(self, team, value):
        max_value = 0
        for team in self.list:
            if team.attributs[value] > max_value:
                max_value = team.attributs[value]

        return max_value


def search_team_in_file_by_name(file_path, name):
    file_to_read = open(file_path, "r")
    team_result = Team()
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
            team_result[tag] = fast_search_value(tag, line)
            if team_result[tag] == name:
                to_return = True
            else:
                storing = False
        elif storing:
            team_result[tag] = fast_search_value(tag, line)
    raise Exception("Critical Error: EOF reaches without finding closing tag.")


def fast_search_tag(line):
    return line[line.find("<") + 1:line.find(">")]


def fast_search_value(tag, line):
    """
    Doesn't search the tag,just get the value in the line for the tag.
    tag variable is here only to accelerate the process !
    """
    return line[line.find(">") + 1:  line.rfind("<")]

