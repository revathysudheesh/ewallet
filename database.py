import json

def load_config(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    database_config = config.get('db', {})
    db_host=database_config.get('host',None)
    db_username=database_config.get('username',None)
    db_password=database_config.get('password',None)
    db_port=database_config.get('port',None)
    db_database=database_config.get('database',None)
    return f'postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}'
