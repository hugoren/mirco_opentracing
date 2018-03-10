# -*- coding: utf-8 -*-

import os

"""
Basic config
"""
DB_CONFIG = {
    'host':  os.environ.get('POSTGRES_SERVICE_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_SERVICE_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_SERVICE_PASSWORD', None),
    'port': os.environ.get('POSTGRES_SERVICE_PORT', 5432),
    'database': os.environ.get('POSTGRES_SERVICE_DB_NAME', 'postgres')
}

ZIPKIN_SERVER = os.environ.get('ZIPKIN_SERVER', None)
ACCESS_CONTROL_ALLOW_ORIGIN = os.environ.get("ACCESS_CONTROL_ALLOW_ORIGIN", "")
ACCESS_CONTROL_ALLOW_HEADERS = os.environ.get("ACCESS_CONTROL_ALLOW_HEADERS", "")
ACCESS_CONTROL_ALLOW_METHODS = os.environ.get("ACCESS_CONTROL_ALLOW_METHODS", "")


env = os.getenv('ENV')

if env == 'test':
    HOST = '192.168.0.108'
    PORT = 20000
    TOKEN = 'b0350c8c75ddcd99738df4c9346bec48dc9c4914'


elif env == 'prod':
    HOST = '192.168.0.103'
    PORT = 9200
    TOKEN = 'b0350c8c75ddcd99738df4c9346bec48dc9c4914'

else:
    HOST = '0.0.0.0'
    PORT = 5454
    TOKEN = 'b0350c8c75ddcd99738df4c9346bec48dc9c4914'
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 0




