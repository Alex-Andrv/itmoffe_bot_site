import configparser

VERSION = '0.0.1'

import os
print(os.getcwd())

SITE_INI_PATH = './config/site_docker.ini'

config = configparser.ConfigParser()
config.read(SITE_INI_PATH)

DEBUG_FLAG_FROM_INI = config['site']['debug'] == 'True'
SECRET_KEY_FROM_INI = config['site']['secret_key']

CLIENT_ID = config['token']["client_id"]
CLIENT_SECRET = config['token']["client_secret"]

DB_PASSWORD = config['db']['password']
DB_NAME = config['db']['database']
DB_HOST = config['db']['host']
DB_USER = config['db']['user']
DB_PORT = int(config['db']['port'])


ALARM_BOT_TOKEN = config['alarm_bot']['token']

CHAT_ID_ALARM = config['alarm_bot']['chat_id']
CHAT_ID_ALARM_WITH_HR = config['alarm_bot']['chat_id_with_HR']
