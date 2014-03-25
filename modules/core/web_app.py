import json

from flask import request, Response, redirect
from flask.templating import render_template
import time

from modules.database.boinc_mongo import (get_collection,
                                          get_all_project,
                                          register_a_project,
                                          get_projects_custom,
                                          update_a_project,
                                          remove_a_project,
                                          get_server_date,
                                          get_all_project_by_date, identification, add_user_session_uuid, get_user_by_session_id)
from modules.database.logging import (get_all_log_harvester)
from modules.boinc.stat_file_operation import ProjectConfiguration
from modules.core.harvesting_function import list_functions
from modules.database.mongodb_operations_low import db

from flask import Flask



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

@app.route('/harvester/login')
def login():
    parameter = request.args
    cookies = request.cookies
    if "username" in parameter and "password" in parameter:
        if identification(parameter["username"], parameter["password"]):
            if not "login" in request.url:
                my_responses = redirect(request.url)
            else:
                my_responses = Response()
                my_responses.set_data(render_template('harvester_main_view.html', logs={}))
            my_uuid = add_user_session_uuid(parameter["username"])
            my_responses.set_cookie("session_id", str(my_uuid) )

            return my_responses

    return render_template('login_view.html')



def must_be_login(f):
    def test_log():
        if "session_id" in request.cookies:
            user = get_user_by_session_id(request.cookies["session_id"])
            if not user:
                return login()
            else:
                try:
                    if time.time() - 3600 > user["session_id_time"]:
                        db["ASFBAH"]["USERS"].update({"name": user["name"]}, {"$unset": {"session_id": ""}})
                        db["ASFBAH"]["USERS"].update({"name": user["name"]}, {"$unset": {"session_id_time": ""}})
                        return login()
                    else:
                        return f()
                except:
                    return login()
        else:
            return login()


    return test_log

@app.route('/harvester/admin')
@must_be_login
def harvester_admin():
    projects_to_print = get_all_project()[:]
    return render_template('harvester_admin_view.html', projects=projects_to_print,
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
        remove_a_project(parameter_ajax["id"])
        return json.dumps("The project has been deleted")
    else:
        return json.dumps("Complete chaos, no Id !")


@app.route('/harvester/admin/projectoperation')
def ajax_project_operation_addition():
    parameter_ajax = request.args
    new_project = ProjectConfiguration()
    if "id" in parameter_ajax:
        if parameter_ajax["id"].startswith("id"):
            parameter_ajax = parameter_ajax[2:]
        if parameter_ajax["id"] == "-1":
            if get_projects_custom(name=parameter_ajax["name"]).count() == 0:
                for parameter in parameter_ajax:
                    if parameter != "id":
                        new_project[parameter] = parameter_ajax[parameter]
                register_a_project(new_project)
                return json.dumps("The project has been correctly added to the database")
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
                update_a_project({'_id': parameter_ajax['id']}, update_dict)
                return json.dumps("Update of the project is a success")
    else:
        return json.dumps("Complete chaos, no Id ! ")


@app.route('/harvester/log')
def get_harvesting_log():
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
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
