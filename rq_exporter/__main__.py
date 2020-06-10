"""
Main Entrypoint.

Usage:

    $ # Start the HTTP server
    $ python -m rq_exporter

    $ # Start the HTTP server on a specific port and host
    $ python -m rq_exporter --host localhost --port 8080

    $ # Set Redis host and password
    $ python -m rq_exporter --redis-host 192.168.1.10 --redis-pass 123456

    $ # Set Redis URL
    $ python -m rq_exporter --redis-url redis://:123456@redis_host:6379/0

"""

import sys
import signal
import time
import logging
import argparse

from prometheus_client import start_wsgi_server
from prometheus_client.core import REGISTRY
from redis.exceptions import RedisError
from rq.utils import import_attribute

from .collector import RQCollector
from .utils import get_redis_connection
from . import config
from .__version__ import __version__


logger = logging.getLogger(__package__)


def parse_args():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog = 'rq-exporter',
        description = 'Python RQ Prometheus Exporter'
    )

    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{__version__}')

    parser.add_argument(
        '--host',
        dest = 'host',
        type = str,
        default = config.HOST,
        metavar = 'HOST',
        required = False,
        help = f'Serve the exporter on this host (Default: {config.DEFAULT_HOST})'
    )

    parser.add_argument(
        '-p', '--port',
        dest = 'port',
        type = int,
        default = config.PORT,
        metavar = 'PORT',
        required = False,
        help = f'Serve the exporter on this port (Default: {config.DEFAULT_PORT})'
    )

    parser.add_argument(
        '--redis-url',
        dest = 'redis_url',
        type = str,
        default = config.REDIS_URL,
        metavar = 'redis://:{password}@{host}:{port}/{db}',
        required = False,
        help = f'Redis server URL (Default: {config.DEFAULT_REDIS_URL})'
    )

    parser.add_argument(
        '--redis-host',
        dest = 'redis_host',
        type = str,
        default = config.REDIS_HOST,
        metavar = 'HOSTNAME',
        required = False,
        help = f'Redis server hostname (Default: {config.DEFAULT_REDIS_HOST})'
    )

    parser.add_argument(
        '--redis-port',
        dest = 'redis_port',
        type = int,
        default = config.REDIS_PORT,
        metavar = 'PORT',
        required = False,
        help = f'Redis server port number (Default: {config.DEFAULT_REDIS_PORT})'
    )

    parser.add_argument(
        '--redis-db',
        dest = 'redis_db',
        type = int,
        default = config.REDIS_DB,
        metavar = 'DB',
        required = False,
        help = f'Redis database number (Default: {config.DEFAULT_REDIS_DB})'
    )

    parser.add_argument(
        '--redis-pass',
        dest = 'redis_pass',
        type = str,
        default = config.REDIS_PASS,
        metavar = 'PASSWORD',
        required = False,
        help = f'Redis server password (Default: {config.DEFAULT_REDIS_PASS})'
    )

    parser.add_argument(
        '--redis-pass-file',
        dest = 'redis_pass_file',
        type = str,
        default = config.REDIS_PASS_FILE,
        metavar = 'FILE_PATH',
        required = False,
        help = f'Redis server password file path (Default: {config.DEFAULT_REDIS_PASS_FILE})'
    )

    parser.add_argument(
        '--worker-class',
        dest = 'worker_class',
        type = str,
        default = config.RQ_WORKER_CLASS,
        metavar = 'module.CustomWorker',
        required = False,
        help = f'RQ Worker class (Default: {config.DEFAULT_WORKER_CLASS})'
    )

    parser.add_argument(
        '--queue-class',
        dest = 'queue_class',
        type = str,
        default = config.RQ_QUEUE_CLASS,
        metavar = 'module.CustomQueue',
        required = False,
        help = f'RQ Queue class (Default: {config.DEFAULT_QUEUE_CLASS})'
    )

    parser.add_argument(
        '--log-level',
        dest = 'log_level',
        type = str,
        default = config.LOG_LEVEL,
        metavar = 'LEVEL',
        required = False,
        help = f'Logging level (Default: {config.DEFAULT_LOG_LEVEL})'
    )

    parser.add_argument(
        '--log-format',
        dest = 'log_format',
        type = str,
        default = config.LOG_FORMAT,
        metavar = 'FORMAT',
        required = False,
        help = f'Logging format string'
    )

    parser.add_argument(
        '--log-datefmt',
        dest = 'log_datefmt',
        type = str,
        default = config.LOG_DATEFMT,
        metavar = 'DATE_FORMAT',
        required = False,
        help = f'Logging date/time format string'
    )

    return parser.parse_args()


def main():
    """Register the RQ collector and start a WSGI server."""
    args = parse_args()

    logging.basicConfig(
        format = args.log_format,
        datefmt = args.log_datefmt,
        level = args.log_level.upper()
    )

    # Register the RQ collector
    try:
        connection = get_redis_connection(
            url = args.redis_url,
            host = args.redis_host,
            port = args.redis_port,
            db = args.redis_db,
            password = args.redis_pass,
            password_file = args.redis_pass_file
        )

        worker_class = import_attribute(args.worker_class)
        queue_class = import_attribute(args.queue_class)

        # Register the RQ collector
        # The `collect` method is called on registration
        REGISTRY.register(RQCollector(connection, worker_class, queue_class))
    except (IOError, RedisError) as exc:
        logger.exception('There was an error starting the RQ exporter')
        sys.exit(1)
    except (ImportError, AttributeError) as exc:
        logger.exception('Incorrect RQ class location')
        sys.exit(1)

    # Start the WSGI server
    start_wsgi_server(args.port, args.host)

    logger.info(f'Serving the application on {args.host}:{args.port}')

    while True:
        time.sleep(1)


if __name__ == '__main__':
    def signal_handler(sig, frame):
        logger.info('Stopping the server...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
