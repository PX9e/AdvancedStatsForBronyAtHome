import json

from flask import Flask, request
from flask.templating import render_template

from modules.database.boinc_mongo import (get_collection,
                                          get_all_project,
                                          register_a_project)
from modules.database.logging import (get_all_log_harvester)
from modules.boinc.stat_file_operation import ProjectConfiguration
from modules.core.harvesting_function import list_functions


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world'


@app.route('/stats/<project>')
def app_get_stats(project):
    res = ""
    for i in get_collection(project):
        res += str(i)
    return res


@app.route('/harvester/admin')
def harvester_admin():
    return render_template('harvester_admin_view.html', projects=get_all_project(),
                           list_function=list_functions)


@app.route('/harvester')
def harvester_main():
    list_of_logs = get_all_log_harvester(20)
    list_log = []
    for log in list_of_logs:
        log_proc = log
        log_proc["datetime"] = str(log_proc["datetime"])
        list_log.append(log_proc)

    return render_template('harvester_main_view.html', logs=list_log)


@app.route('/harvester/admin/projectoperation')
def ajax_projext_operation():
    parameter_ajax = request.args
    if "id" in parameter_ajax:
        if parameter_ajax["id"].startswith("id"):
            parameter_ajax = parameter_ajax[2:]
        if parameter_ajax["id"] == "-1":
            new_project = ProjectConfiguration()
            for parameter in parameter_ajax:
                if parameter != "id":
                    new_project[parameter] = parameter_ajax[parameter]
            register_a_project(new_project)
        else:
            o = 0


@app.route('/harvester/log')
def get_harvesting_log():
    res = []
    list_of_logs = get_all_log_harvester(parameter_ajax=request.args)
    try:
        for log in list_of_logs:
            log_proc = log
            log_proc["datetime"] = str(log_proc["datetime"])
            del log_proc["_id"]
            res.append(log_proc)
        return json.dumps(res)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)