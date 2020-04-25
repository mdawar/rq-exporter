"""
Sample queues for testing.

"""

import os
from redis import Redis
from rq import Queue


# Redis connection
redis_connection = Redis(
    host = os.environ.get('RQ_REDIS_HOST', 'localhost'),
    port = os.environ.get('RQ_REDIS_PORT', '6379'),
    db = os.environ.get('RQ_REDIS_DB', '0'),
    password = os.environ.get('RQ_REDIS_PASS')
)


# Queues
default = Queue(connection=redis_connection)
high = Queue('high', connection=redis_connection)
low = Queue('low', connection=redis_connection)
