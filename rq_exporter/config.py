"""
RQ exporter configuration.

"""

import os
from rq.defaults import DEFAULT_QUEUE_CLASS, DEFAULT_WORKER_CLASS


# Defaults
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '9726'
DEFAULT_REDIS_URL = None
DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = '6379'
DEFAULT_REDIS_DB = '0'
DEFAULT_REDIS_PASS = None
DEFAULT_REDIS_PASS_FILE = None
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_FORMAT = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s'
DEFAULT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

# RQ classes
RQ_WORKER_CLASS = os.environ.get('RQ_WORKER_CLASS', DEFAULT_WORKER_CLASS)
RQ_QUEUE_CLASS = os.environ.get('RQ_QUEUE_CLASS', DEFAULT_QUEUE_CLASS)

# Exporter config
HOST = os.environ.get('RQ_EXPORTER_HOST', DEFAULT_HOST)
PORT = os.environ.get('RQ_EXPORTER_PORT', DEFAULT_PORT)

# Redis config
REDIS_URL = os.environ.get('RQ_REDIS_URL', DEFAULT_REDIS_URL)
# These configuration options will be ignored if the URL is set
REDIS_HOST = os.environ.get('RQ_REDIS_HOST', DEFAULT_REDIS_HOST)
REDIS_PORT = os.environ.get('RQ_REDIS_PORT', DEFAULT_REDIS_PORT)
REDIS_DB = os.environ.get('RQ_REDIS_DB', DEFAULT_REDIS_DB)
REDIS_PASS = os.environ.get('RQ_REDIS_PASS', DEFAULT_REDIS_PASS)
REDIS_PASS_FILE = os.environ.get('RQ_REDIS_PASS_FILE', DEFAULT_REDIS_PASS_FILE)

# Logging config
LOG_LEVEL = os.environ.get('RQ_EXPORTER_LOG_LEVEL', DEFAULT_LOG_LEVEL).upper()
LOG_FORMAT = os.environ.get('RQ_EXPORTER_LOG_FORMAT', DEFAULT_LOG_FORMAT)
LOG_DATEFMT = os.environ.get('RQ_EXPORTER_LOG_DATEFMT', DEFAULT_LOG_DATEFMT)
