"""
RQ exporter utility functions.

"""

from redis import Redis
from rq import Queue, Worker
from rq.job import JobStatus

from . import config


def get_redis_connection():
    """Get the Redis connection instance.

    Returns:
        redis.Redis: Redis connection instance.

    Raises:
        IOError: On errors opening the password file.

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


def get_workers_stats(connection=None):
    """Get the RQ workers stats.

    Args:
        connection (redis.Redis): Redis connection instance

    Returns:
        list: List of worker stats as a dict {name, queues, state}

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    workers = Worker.all(connection=connection)

    return [
        {
            'name': w.name,
            'queues': [q.name for q in w.queues],
            'state': w.get_state()
        }
        for w in workers
    ]


def get_queue_jobs(queue_name, connection=None):
    """Get the jobs by status of a Queue.

    Args:
        queue_name (str): The RQ Queue name
        connection (redis.Redis): Redis connection instance

    Returns:
        dict: Number of jobs by job status

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue = Queue(queue_name, connection=connection)

    return {
        JobStatus.QUEUED: queue.count,
        JobStatus.STARTED: queue.started_job_registry.count,
        JobStatus.FINISHED: queue.finished_job_registry.count,
        JobStatus.FAILED: queue.failed_job_registry.count,
        JobStatus.DEFERRED: queue.deferred_job_registry.count,
        JobStatus.SCHEDULED: queue.scheduled_job_registry.count
    }


def get_jobs_by_queue(connection=None):
    """Get the current jobs by queue.

    Args:
        connection (redis.Redis): Redis connection instance

    Returns:
        dict: Dictionary of job count by status for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queues = Queue.all(connection=connection)

    return {
        q.name: get_queue_jobs(q.name, connection) for q in queues
    }
