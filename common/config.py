import os

SECRETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.path.pardir,
                            "secrets")


def get_config():
    config = {
        'kafka': {
            'service_uri': 'kafka-1654c119-sergey-01ea.aivencloud.com:21772',
            'ca_path': os.path.join(SECRETS_PATH, 'ca_certificate.pem'),
            'cert_path': os.path.join(SECRETS_PATH, 'access_certificate.cert'),
            'key_path': os.path.join(SECRETS_PATH, 'access_key.key'),
            'group_id': 'main',
            'client_id': 'metrics_consumer',
            'partition_count': 2,
            'partition': os.environ.get('partition')
        },
        'pg': {
            'user': 'avnadmin',
            'host': 'pg-3d696816-sergey-01ea.aivencloud.com',
            'port': '21770',
            'password': 'h9z5brqtsel553zo',
        },
        'group_name': os.environ.get('group_name'),
        'check_interval': 5
    }
    if os.environ.get('env') == 'prod':
        config['kafka'].update({'topic': 'metrics'})
        config['pg'].update({'dbname': 'site_metrics'})
    else:
        config['kafka'].update({'topic': 'debug'})
        config['pg'].update({'dbname': 'debug_db'})
    return config
