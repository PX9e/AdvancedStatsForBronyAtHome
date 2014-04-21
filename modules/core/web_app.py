# coding=utf-8


import json

from flask import (request,
                   Response,
)
from flask.templating import render_template

from modules.database.boinc_mongo import (get_collection,
                                          get_all_project,
                                          register_a_project,
                                          get_projects_custom,
                                          update_a_project,
                                          remove_a_project,
                                          get_server_date,
                                          get_all_project_by_date,
                                          identification,
                                          add_user_session_uuid,
)
from modules.database.logging import (get_all_log_harvester,
)
from modules.boinc.stat_file_operation import ProjectConfiguration
from modules.core.harvesting_function import list_functions

from flask import Flask
import flask_login


app = Flask(__name__)


@app.route('/stats/<project>')
def app_get_stats(project):
    res = ""
    for i in get_collection(project):
        res += str(i)
    return res


@app.route('/harvester/projects')
def harvester_projects():
    parameter_ajax = request.args
    if "date" in parameter_ajax:
        projects = get_all_project_by_date(parameter_ajax["date"])
    else:
        projects = get_all_project()[:]
    projects_to_send = []
    for i in projects:
        i["_id"] = str(i["_id"])
        projects_to_send.append(i)
    return json.dumps(projects_to_send)


@app.route('/harvester/server_time')
def harvester_server_time():
    return json.dumps(get_server_date())


@app.route('/harvester/login', methods=["GET", "POST"])
def login():
    parameter = request.args
    cookies = request.cookies
    if "username" in parameter and "password" in parameter:
        if identification(parameter["username"], parameter["password"]):
            my_responses = Response()
            my_responses.set_data(render_template('harvester_main_view.html',
                                                  logs={}))
            my_uuid = add_user_session_uuid(parameter["username"])
            my_responses.set_cookie("session_id", str(my_uuid))
            return my_responses
    return render_template('login_view.html')


@app.route('/harvester/admin')
def harvester_admin():
    projects_to_print = []
    for i in get_all_project():
        projects_to_print.append(i)
    return render_template('harvester_admin_view.html',
                           projects=projects_to_print,
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


@app.route('/harvester/admin/projectdeletion')
def ajax_project_operation_deletion():
    parameter_ajax = request.args
    if "id" in parameter_ajax:
        if parameter_ajax["id"].startswith("id"):
            parameter_ajax["id"] = parameter_ajax["id"][2:]
        result = remove_a_project(parameter_ajax["id"])
        if result["err"] is None:
            return json.dumps({"text":
                                   "The project has been deleted",
                               "type":
                                   "success"})
        else:
            return json.dumps({"text":
                                   "The project has not been deleted, error is:" +
                                   str(result["err"]),
                               "type":
                                   "error"})
    else:
        return json.dumps({"text":
                               "Complete chaos, no Id ! ",
                           "type":
                               "error"})


@app.route('/harvester/admin/projectoperation')
def ajax_project_operation_addition():
    parameter_ajax = request.args
    if "id" in parameter_ajax:
        if parameter_ajax["id"].startswith("id"):
            parameter_ajax = parameter_ajax[2:]
        if parameter_ajax["id"] == "-1":
            if get_projects_custom(name=parameter_ajax["name"]).count() == 0:
                parameter_ajax = dict(parameter_ajax)
                del parameter_ajax["id"]
                for param in parameter_ajax:
                    if isinstance(parameter_ajax[param], list):
                        if len(parameter_ajax[param]) == 1:
                            parameter_ajax[param] = parameter_ajax[param][0]
                new_project = ProjectConfiguration(**parameter_ajax)
                result = register_a_project(new_project)
                if result is not None:
                    return json.dumps(
                        {"text":
                             "The project has been correctly added to the database",
                         "type":
                             "success"})
                else:
                    return json.dumps(
                        {"text":
                             "The project has NOT been correctly added to the database",
                         "type":
                             "error"})
            else:
                return json.dumps("A project already have this name !")
        else:
            if get_projects_custom(_id=parameter_ajax["id"]).count() == 0:
                return json.dumps("Complete chaos, Id is not matching !")
            else:
                update_dict = {}
                for parameter in parameter_ajax:
                    if parameter != "id":
                        update_dict[parameter] = parameter_ajax[parameter]
                result = update_a_project({'_id': parameter_ajax['id']},
                                          update_dict)
                if result["err"] is None:
                    return json.dumps(
                        {"text":
                             "Update of the project is a success",
                         "type":
                             "success"})
                else:
                    return json.dumps(
                        {"text":
                             "Update of the project failed, error is:" + str(
                                 result["err"]),
                         "type":
                             "error"})
    else:
        return json.dumps({"text":
                               "Complete chaos, no Id ! ",
                           "type":
                               "error"})


@app.route('/harvester/log')
def get_harvesting_log():
    """
    Return the list of logs without the _id of the log.
    It is used to print a table of logs messages, logged before.

    :return: list or str
    """
    res = []
    list_of_logs = get_all_log_harvester(parameter_ajax=request.args)
    try:
        for log in list_of_logs:
            log_proc = log
            del log_proc["_id"]
            res.append(log_proc)
        return json.dumps(res)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
