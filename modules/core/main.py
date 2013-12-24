
from modules.network.http_request_high_level import download_file
from modules.utils.decompression import decompression_gz

from modules.boinc.stat_file_operation import search_team_in_file_by_name

from modules.database.boinc_mongo import (register_team_state_in_database,
                                          get_collection)

from modules.utils.config import config
def main():
    #download_file("team.gz", "http://www.gpugrid.net/stats/team.gz")
    file_pr = decompression_gz("team.gz", False)
    team = search_team_in_file_by_name(file_pr, "Brony@Home")
    register_team_state_in_database(team, "gpugrid")
    print(str(team))
    A = list(get_collection("project_stats", "gpugrid").find({}))
    print(str(len(A)))
    print(A)


#Here we go
if __name__ == "__main__":
    main()