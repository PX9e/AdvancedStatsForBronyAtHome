from flask import Flask, jsonify, request
from flask.templating import render_template
from modules.database.boinc_mongo import get_collection
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
    o=0

@app.route('/harvester')
def harvester_main():
    list_of_logs = get_all_log_harvester(20)
    list_log = []
    for log in list_of_logs:
        log_proc = log
        log_proc["datetime"] = str(log_proc["datetime"])
        list_log.append(log_proc)

    return render_template('harvester_main_view.html', logs=list_log)

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