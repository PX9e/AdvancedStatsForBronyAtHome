from pymongo import MongoClient


def connect(address=None):
    global client
    if address:
        client = MongoClient(address)
    else:
        client = MongoClient()

    return client


def connection_on_database(database_name):
    return db[database_name]

def kill():
    db.close()


db = None

db = connect()