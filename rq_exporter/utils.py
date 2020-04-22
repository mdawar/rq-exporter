"""
RQ exporter utility functions.

"""

from redis import Redis

from . import config


def get_redis_connection():
    """Get the Redis connection instance.

    Raises:
        IOError: On errors opening the password file.

    Returns:
        redis.Redis: Redis connection instance.

    """
    if config.REDIS_URL:
        return Redis.from_url(config.REDIS_URL)

    REDIS_AUTH = config.REDIS_AUTH

    # Use password file if provided
    if config.REDIS_AUTH_FILE:
        with open(config.REDIS_AUTH_FILE, 'r') as auth_file:
            REDIS_AUTH = auth_file.read().strip()

    return Redis(
        host = config.REDIS_HOST,
        port = config.REDIS_PORT,
        db = config.REDIS_DB,
        password = REDIS_AUTH
    )
