"""
Sample queues for testing.

"""

import os
from redis import Redis
from rq import Queue
from custom import CustomQueue


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

# Queues using a custom Queue class
custom_default = CustomQueue(connection=redis_connection)
custom_high = CustomQueue('high', connection=redis_connection)
custom_low = CustomQueue('low', connection=redis_connection)
