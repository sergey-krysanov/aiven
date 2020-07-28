import os

SECRETS_PATH = '/Users/sergiikrysanov/home/CV/Applications/Aiven/src/secrets'


def get_config():
    config = {
        'kafka': {
            'SERVICE_URI': 'kafka-1654c119-sergey-01ea.aivencloud.com:21772',
            'CA_PATH': os.path.join(SECRETS_PATH, 'ca_certificate.pem'),
            'CERT_PATH': os.path.join(SECRETS_PATH, 'access_certificate.cert'),
            'KEY_PATH': os.path.join(SECRETS_PATH, 'access_key.key'),
            'group_id': 'main_group',
            'client_id': 'metrics_consumer',
        },
        'pg': {
            'user': 'avnadmin',
            'host': 'pg-3d696816-sergey-01ea.aivencloud.com',
            'port': '21770',
            'password': 'h9z5brqtsel553zo',
        },
        'group_id': os.environ.get('GROUP_ID', 'common'),
        'check_interval': 5
    }
    if os.environ.get('env') == 'prod':
        config['kafka'].update({'TOPIC': 'metrics'})
        config['pg'].update({'dbname': 'site_metrics'})
    else:
        config['kafka'].update({'TOPIC': 'debug'})
        config['pg'].update({'dbname': 'debug_db'})
    return config
