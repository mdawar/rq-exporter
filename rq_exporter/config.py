"""
RQ exporter configuration.

"""

import os


REDIS_URL = os.environ.get('RQ_REDIS_URL')

# These configuration options will be ignored if the URL is set
REDIS_HOST = os.environ.get('RQ_REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('RQ_REDIS_PORT', '6379')
REDIS_DB = os.environ.get('RQ_REDIS_DB', '0')
REDIS_AUTH = os.environ.get('RQ_REDIS_AUTH')
REDIS_AUTH_FILE = os.environ.get('RQ_REDIS_AUTH_FILE')

# Logging level (Only used when executing the package)
LOG_LEVEL = os.environ.get('RQ_EXPORTER_LOG_LEVEL', 'INFO').upper()
