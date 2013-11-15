from pymongo import MongoClient


def connect(address=None):
    global client
    if address:
        client = MongoClient(address)
    else:
        client = MongoClient()

    return client


def connection_on_database(database_name):
    global connection
    return connection[database_name]


def get_collection(database_name, name):
    return connection[database_name][name]


def kill():
    global connection
    connection.close()


connection = None

connection = connect()