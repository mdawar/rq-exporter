from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY
from redis import Redis

from .collector import RQCollector
from . import config


if config.REDIS_URL:
    redis_connection = Redis.from_url(config.REDIS_URL)
else:
    REDIS_AUTH = config.REDIS_AUTH

    # Use password file if provided
    if config.REDIS_AUTH_FILE:
        try:
            with open(config.REDIS_AUTH_FILE, 'r') as auth_file:
                REDIS_AUTH = auth_file.read().strip()
        except IOError as err:
            print(err)

    redis_connection = Redis(
        host = config.REDIS_HOST,
        port = config.REDIS_PORT,
        db = config.REDIS_DB,
        password = REDIS_AUTH
    )


# Register the RQ collector
REGISTRY.register(RQCollector(redis_connection))


"""
WSGI Application.

"""
app = make_wsgi_app()
