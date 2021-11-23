import psycopg2
from configparser import ConfigParser
import os
config = ConfigParser()

if os.name == 'posix':
    config.read('/var/www/qlair-dashboard/dashboard/main/config/config.ini')
else:
    config.read('main/config/config.ini')


def get_connection_local():
    return psycopg2.connect(host='localhost', user='postgres',
                            password='**', dbname='ourairdb')


def get_connection():
    return psycopg2.connect(
            host=config['postgres']['host'], user=config['postgres']['user'],
            password=config['postgres']['password'], dbname=config['postgres']['dbname'])

