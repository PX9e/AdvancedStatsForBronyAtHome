# coding=utf-8

from time import sleep
from modules.database.boinc_mongo import (get_user,
                                          add_user,
                                          )
from modules.utils.config import (config,
                                  generate_secret_key,
                                  )

import os

if __name__ == "__main__":
    print("Core Ignition Starting...")
    #give the time to cancel in case of error !
    sleep(5)
    A = "a"
    B = "b"

    if not "SECRET_KEY" in config["ASFBAH"]:
        config["ASFBAH"]["SECRET_KEY"] = generate_secret_key(256)
        config.write(open("asfbah.config", "r+"))

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
    from modules.core.harvester import Harvester
    Harvester()
    print("Launching Gunicorn")
    os.popen("gunicorn web_app:app -w 3 -b 0.0.0.0:5000")
