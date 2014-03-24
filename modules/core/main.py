
from time import sleep
from modules.database.boinc_mongo import get_user, add_user
from modules.utils.config import (config,
                                  generate_secret_key)

if __name__ == "__main__":

    print("Core Ignition Starting...")
    #give the time to cancel in case of error !
    sleep(2)
    A = "a"
    B = "b"
    import os

    if not "SECRET_KEY" in config["ASFBAH"]:
        config["ASFBAH"]["SECRET_KEY"] = generate_secret_key(256)
        config.write(open("asfbah.config", "r+"))

    print("Launching Harvester")
    user = get_user("Admin")
    if user:
        os.popen("python3 modules/core/harvester_launch.py")
        print("Launching Gunicorn")
        os.popen("gunicorn  --chdir modules/core/  web_app:app -w 3 -b 0.0.0.0")
    else:

        print("No user Admin")
        print("Creation ...")
        while A != B and len(A) < 8:
            print("Password?")
            A = input()
            print("Confirm password?")
            B = input()
            if A != B:
                print("password different retry")
                print("password too short")
            try:
                if len(A) < 8:
                    print("password too short")
            except:
                print("password too short")

        add_user("Admin", A)