# coding=utf-8
from time import sleep
import os

from ASFBAH.database.boinc_mongo import get_user, add_user
from ASFBAH.utils.config import config, generate_secret_key, realpath


if __name__ == "__main__":
    print("Core Ignition Starting...")

    A = "a"
    B = "b"

    if not "SECRET_KEY" in config["ASFBAH"]:
        config["ASFBAH"]["SECRET_KEY"] = generate_secret_key(256)
        config.write(open(realpath + "asfbah.conf", "r+"))
    user = get_user("Admin")
    if not user:
        print("No user Admin")
        print("Creation ...")
        while A != B or len(A) < 8:
            print("Password?")
            A = input()
            print("Confirm password?")
            B = input()
            if A != B:
                print("password different retry")
            try:
                if len(A) < 8:
                    print("password too short")
            except:
                print("password error")

        add_user("Admin", A)

    user = get_user("Admin")
    print("Launching Harvester")
    from ASFBAH.core.harvester import Harvester
    Harvester()
    print("Launching Gunicorn")
    realpath_execution = os.path.realpath(__file__)
    realpath_execution = realpath_execution[:realpath_execution.rfind(os.sep)]

    os.popen("gunicorn --chdir {0} web_app:app -w 3 -b 0.0.0.0:5000".format(realpath_execution))
