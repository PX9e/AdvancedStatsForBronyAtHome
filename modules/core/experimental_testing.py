from network.http_request_high_level import download_file
from utils.decompression import decompression_gz

from boinc.stat_file_operation import search_team_in_file_by_name

import timeit
download_file("team.gz","http://www.gpugrid.net/stats/team.gz")
file_pr = decompression_gz("team.gz", False)
team = search_team_in_file_by_name(file_pr, "Brony@Home")
print team


timeit.timeit(search_team_in_file_by_name(file_pr, "Brony@Home"))