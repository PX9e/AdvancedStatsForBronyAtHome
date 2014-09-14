# coding=utf-8


import json

from flask import request, Response
from flask.templating import render_template
from flask import Flask
from flask_login import LoginManager, login_required, login_user

from ASFBAH.database.boinc_mongo import (get_collection, get_all_project,
                                          register_a_project,
                                          get_projects_custom, update_a_project,
                                          remove_a_project, get_server_date,
                                          get_all_project_by_date,
                                          identification, add_user_session_uuid,
                                          get_list_all_project,
                                          get_list_all_user)
from ASFBAH.database.logging import get_all_log_harvester
from ASFBAH.boinc.stat_file_operation import ProjectConfiguration
from ASFBAH.core.harvesting_function import list_functions
from ASFBAH.utils.config import config


app = Flask(__name__)

app.secret_key = config["ASFBAH"]["SECRET_KEY"]
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/harvester/login"


@app.route('/stats/<project>')
def app_get_stats(project):
    return json.dumps(get_collection(project))


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
    if request.method == "POST":
        if identification(request.form["username"], request.form["password"]):
            from ASFBAH.utils.users import user

            my_responses = Response()
            my_responses.set_data(render_template('harvester_main_view.html',
                                                  logs={}))
            my_user = add_user_session_uuid(request.form["username"])
            login_user(user(my_user))
            return my_responses
        else:
            return render_template('login_view.html', message="Password or "
                                                       "username invalid")
    return render_template('login_view.html')


@app.route('/harvester/admin')
@login_required
def harvester_admin():
    projects_to_print = []
    for i in get_all_project():
        projects_to_print.append(i)
    return render_template('harvester_admin_view.html',
                           projects=projects_to_print,
                           list_function=list_functions)

@app.route('/stats/summary')
def get_summary():
    o=0

@app.route('/')
def root():
    projects_per_category = {}
    projects_list = get_list_all_project()

    for project in projects_list:
        if project["category"] in projects_per_category:
            projects_per_category[project["category"]].append(project)
        else:
            projects_per_category[project["category"]] = [project]

    return render_template('main_page.html', projects=projects_per_category, users=get_list_all_user())


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
                                   "The project has not been deleted, "
                                   "error is:" +
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
                             "The project has been correctly added to the "
                             "database",
                         "type":
                             "success"})
                else:
                    return json.dumps(
                        {"text":
                             "The project has NOT been correctly added to the "
                             "database",
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


@login_manager.user_loader
def load_user(userid):
    from ASFBAH.database.boinc_mongo import db
    from ASFBAH.utils.users import user

    users = db["ASFBAH"]["USERS"].find({"session_id": userid})
    if users.count() > 0:
        return user(users[0])
    else:
        return None


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=True)
