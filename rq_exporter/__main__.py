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

from prometheus_client import start_wsgi_server


def signal_handler(sig, frame):
    print('Stopping the server...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


PORT = 8000

if len(sys.argv) > 1:
    arg = sys.argv[1]

    try:
        PORT = int(sys.argv[1])
    except ValueError as exc:
        print(f'Invalid port number: {arg}')
        sys.exit(1)


start_wsgi_server(PORT)

print(f'Server running on port {PORT}')


while True:
    time.sleep(1)
