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


def register_collector():
    """Register the RQ collector instance.

    Raises:
        IOError: From `get_redis_connection` if there was an error opening
                 the password file.
        redis.exceptions.RedisError: On Redis connection errors.

    """
    # Register the RQ collector
    # The `collect` method is called on registration
    REGISTRY.register(RQCollector(
        get_redis_connection()
    ))


def create_app():
    """Create a WSGI application."""
    register_collector()

    return make_wsgi_app()
