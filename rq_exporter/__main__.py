"""
Main Entrypoint.

Usage:

    $ # Start the HTTP server
    $ python -m rq_exporter

    $ # Start the HTTP server on a specific port
    $ python -m rq_exporter 8080

"""

import sys
import signal
import time
import logging

from prometheus_client import start_wsgi_server
from redis.exceptions import RedisError

from . import register_collector
from . import config


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format = '[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        level = config.LOG_LEVEL
    )


    def signal_handler(sig, frame):
        logger.info('Stopping the server...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    PORT = 8000

    if len(sys.argv) > 1:
        arg = sys.argv[1]

        try:
            PORT = int(sys.argv[1])
        except ValueError as exc:
            logger.error(f'Invalid port number: {arg}')
            sys.exit(1)


    # Register the RQ collector
    try:
        register_collector()
    except (IOError, RedisError) as exc:
        logger.exception('There was an error starting the RQ exporter')
        sys.exit(1)

    # Start the WSGI server
    start_wsgi_server(PORT)

    logger.info(f'Server running on port {PORT}')

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
