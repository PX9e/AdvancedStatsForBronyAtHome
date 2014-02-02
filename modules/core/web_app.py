from flask import Flask, jsonify, request
from flask.templating import render_template
from modules.database.boinc_mongo import (get_collection,
                                          get_all_project)
from modules.database.logging import (get_all_log_harvester,
                                      log_something_harvester)
import json


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
    project_final = []
    for project in get_all_project():
        if not "name" in project:
            project["name"] = "ERROR: name invalid"
        if not "url" in project:
            project["url"] = "ERROR: url invalid"
        if not "representation" in project:
            project["representation"] = "ERROR: representation invalid"
        if not "frequency" in project:
            project["frequency"] = "ERROR: frequency invalid"
        project["_id"] = "id" + str(project["_id"])
        project_final.append(project)
    print(project_final)
    return render_template('harvester_admin_view.html', projects=project_final)


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
    parameter = request.args
    return True

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