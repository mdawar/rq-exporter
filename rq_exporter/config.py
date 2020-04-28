"""
RQ exporter configuration.

"""

import os


REDIS_URL = os.environ.get('RQ_REDIS_URL')

# These configuration options will be ignored if the URL is set
REDIS_HOST = os.environ.get('RQ_REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('RQ_REDIS_PORT', '6379')
REDIS_DB = os.environ.get('RQ_REDIS_DB', '0')
REDIS_PASS = os.environ.get('RQ_REDIS_PASS')
REDIS_PASS_FILE = os.environ.get('RQ_REDIS_PASS_FILE')

# Logging config
LOG_LEVEL = os.environ.get('RQ_EXPORTER_LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.environ.get('RQ_EXPORTER_LOG_FORMAT', '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s')
LOG_DATEFMT = os.environ.get('RQ_EXPORTER_LOG_DATEFMT', '%Y-%m-%d %H:%M:%S')
