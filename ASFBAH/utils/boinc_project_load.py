# coding=utf-8
import time

from ASFBAH.boinc.stat_file_operation import ProjectConfiguration


def load_boinc_project_from_wiki():

    starttime = time.time()
    # html = urlopen("http://boinc.berkeley.edu/wiki/Project_list").read().decode('utf-8')

    file = open("/home/guillaume/Downloads/Project list - BOINC.htm")
    html = file.readlines()
    dict_categories = {}
    project = ProjectConfiguration()
    current_config = None
    indicator_step = 0
    for i in html:
        try:
            if indicator_step == 0:
                if i.index("toclevel-1"):
                    result = extract_toctext(i)
                    dict_categories[result[1]] = result[0]
            if i.index(""):
                o = 0
        except ValueError:
            pass
    print("End of import in {0} seconds".format(time.time() - starttime))


def extract_toctext(html_to_extract):
    motif_a_href = '<a href="'
    motif_span_class = '<span class="toctext">'
    html_temp = html_to_extract
    href = html_temp[html_temp.index(motif_a_href) + len(motif_a_href):]
    href = href[:href.index('">')]
    html_temp = html_temp[html_temp.index(motif_span_class) + len(motif_span_class):]
    value = html_temp[:html_temp.index("</span>")]
    return value, href


class TempProject(object):
    def __init__(self):
        self.anchor = ""
        self.attributs = {"name": "", "description": "", "date_update": 0,
                          "frequency": 3600, "representation": "", "url": "",
                          "harvesting_function": "harvest_boinc_project"}