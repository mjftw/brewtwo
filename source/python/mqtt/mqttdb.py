import json
import time
from argparse import ArgumentParser


from mqtt_listener import MQTTListener


def check_cfg_valid(config):
    if not config:
        raise AttributeError('Invalid config file')
    if 'mqtt' not in config:
        raise AttributeError('Invalid config file')
    if 'password' in config['mqtt'] and 'username' not in config['mqtt']:
        raise AttributeError('Invalid config file')


def set_cfg_defaults(config):
    if 'mqtt' not in config:
        config['mqtt'] = {}
    if 'host' not in config['mqtt']:
        config['mqtt']['host'] = '127.0.0.1'
    if 'port' not in config['mqtt']:
        config['mqtt']['port'] = 1883
    if 'topic' not in config['mqtt']:
        config['mqtt']['topic'] = '#'

    empty_options = [
        'username', 'password', 'client_id'
    ]

    for eo in empty_options:
        if eo not in config['mqtt']:
            config['mqtt'][eo] = None

    return config


def check_cfg_security(config):
    if 'password' in config and str(config['mqtt']['port']) == '1883':
        raise AttributeError(
            'Refusing to connect to insecure MQTT broker when using password')


def load_cfg_json(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    config = set_cfg_defaults(config)
    check_cfg_valid(config)
    if ('allow_insecure' not in config['mqtt'] or
            not config['mqtt']['allow_insecure']):
        check_cfg_security(config)

    return config


def listener_msg_callback(*args, **kwargs):
    print(*args, **kwargs)


def main(config_file):
    cfg = load_cfg_json(config_file)

    listener = MQTTListener(
        on_message=listener_msg_callback,
        topic=cfg['mqtt']['topic'],
        broker_host=cfg['mqtt']['host'],
        broker_port=cfg['mqtt']['port'],
        username=cfg['mqtt']['username'],
        password=cfg['mqtt']['password'],
        client_id=cfg['mqtt']['client_id']
    )

    listener.connect()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Service to listen record MQTT messages to a database')
    parser.add_argument('config_file', type=str,
                        help='Configuration file to use for MQTT broker and '
                        'database connection settings (JSON format)')

    args = parser.parse_args()

    main(args.config_file)
