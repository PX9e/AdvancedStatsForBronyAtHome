from modules.core.harvester import Harvester
from flask import Flask
from time import sleep
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello world'


def main():
    harvester = Harvester()
    app.run(host='0.0.0.0')
    harvester.stop()
    sleep(20)

#Here we go
if __name__ == "__main__":
    main()