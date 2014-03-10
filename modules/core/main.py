from time import sleep

if __name__ == "__main__":
    print("Core Ignition Starting...")
    #give the time to cancel in case of error !
    sleep(5)
    import os
    print("Launching Harvester")
    os.popen("python3 modules/core/harvester_launch.py")
    print("Launching Gunicorn")
    os.popen("gunicorn  --chdir modules/core/  web_app:app -w 3 -b 0.0.0.0")
