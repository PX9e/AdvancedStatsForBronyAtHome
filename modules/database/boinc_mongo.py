from .mongodb_operations_low import db


def register_team_state_in_database(team_state_to_insert, project_name):
    db["ASFBAH"]["project_stats"][project_name].insert(team_state_to_insert.attributs)


def get_collection(database_name, name):
    return db["ASFBAH"][database_name][name]


