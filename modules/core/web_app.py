import json

from flask import Flask, request
from flask.templating import render_template

from modules.database.boinc_mongo import (get_collection,
                                          get_all_project,
                                          register_a_project,
                                          get_projects_custom,
                                          update_a_project,
                                          remove_a_project)
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


@app.route('/harvester/projects')
def harvester_projects():
    projects = get_all_project()[:]
    projects_to_send =[]
    for i in projects:
        i["_id"] = str(i["_id"])
        projects_to_send.append(i)
    return json.dumps(projects_to_send)

@app.route('/harvester/admin')
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
            log_proc["datetime"] = str(log_proc["datetime"])
            del log_proc["_id"]
            res.append(log_proc)
        return json.dumps(res)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)