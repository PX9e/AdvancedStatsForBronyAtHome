from flask import Flask
from modules.database.boinc_mongo import get_collection
from modules.database.logging import (get_all_log,
                                      log_something)


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


@app.route('/harvester/log')
def get_harvesting_log():
    res = ""
    u = get_all_log()
    try:
        for i in range(0, u.count()-1):
            res += str(u[i])
    except Exception as e :
        log_something("Web_App", "TYPE_ERROR", str(e) )
    return res


if __name__ == "__main__":
    app.run(host='0.0.0.0')