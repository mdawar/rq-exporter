"""
RQ exporter module.

Register the RQ collector and create the WSGI application instance.

"""

import sys

from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

from .collector import RQCollector
from .utils import get_redis_connection


"""
Redis connection instance.

"""
try:
    redis_connection = get_redis_connection()
except IOError as exc:
    # TODO: use logging module
    print('Error creating a Redis connection: ', exc)
    sys.exit(1)


# Register the RQ collector
REGISTRY.register(RQCollector(redis_connection))


"""
WSGI Application.

"""
app = make_wsgi_app()
