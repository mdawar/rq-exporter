"""
RQ exporter module.

Register the RQ collector and create the WSGI application instance.

"""

import sys
import logging

from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

from .collector import RQCollector
from .utils import get_redis_connection


logger = logging.getLogger(__name__)


"""
Redis connection instance.

"""
try:
    redis_connection = get_redis_connection()
except IOError:
    logger.exception('Error creating a Redis connection')
    sys.exit(1)


# Register the RQ collector
REGISTRY.register(RQCollector(redis_connection))


"""
WSGI Application.

"""
app = make_wsgi_app()
