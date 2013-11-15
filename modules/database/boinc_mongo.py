from modules.database.mongodb_operations_low import connection, connect
import datetime

def register_team_state_in_database(team_state_to_insert, project_name):
    global connection
    if not connection:
        print "re-connection"
        connection = connect()
    database = connection["project_stats"][project_name]
    database.insert(team_state_to_insert.attributs)