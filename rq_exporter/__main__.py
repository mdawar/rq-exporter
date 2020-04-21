"""
Main Entrypoint:

Usage:

    $ # Start the HTTP server
    $ python -m rq_exporter

"""

import sys
import signal
import time
from prometheus_client import start_http_server


def signal_handler(sig, frame):
    print('Stopping the server...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


start_http_server(8000)


while True:
    time.sleep(1)
