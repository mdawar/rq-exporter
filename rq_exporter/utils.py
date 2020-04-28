"""
RQ exporter utility functions.

"""

from redis import Redis
from rq import Queue, Worker
from rq.job import JobStatus


def get_redis_connection(host='localhost', port='6379', db='0',
                        password=None, password_file=None, url=None):
    """Get the Redis connection instance.

    Note:
        If the `url` is provided, all the other options are ignored.
        If `password_file` is provided it will be used instead of `password.`

    Args:
        host (str): Redis hostname
        port (str, int): Redis server port number
        db (str, int): Redis database number
        password (str): Redis password
        password_file (str): Redis password file path
        url (str): Full Redis connection URL

    Returns:
        redis.Redis: Redis connection instance.

    Raises:
        IOError: On errors opening the password file.

    """
    if url:
        return Redis.from_url(url)

    # Use password file if provided
    if password_file:
        with open(password_file, 'r') as f:
            password = f.read().strip()

    return Redis(host=host, port=port, db=db, password=password)


def get_workers_stats():
    """Get the RQ workers stats.

    Returns:
        list: List of worker stats as a dict {name, queues, state}

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    workers = Worker.all()

    return [
        {
            'name': w.name,
            'queues': w.queue_names(),
            'state': w.get_state()
        }
        for w in workers
    ]


def get_queue_jobs(queue_name):
    """Get the jobs by status of a Queue.

    Args:
        queue_name (str): The RQ Queue name

    Returns:
        dict: Number of jobs by job status

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue = Queue(queue_name)

    return {
        JobStatus.QUEUED: queue.count,
        JobStatus.STARTED: queue.started_job_registry.count,
        JobStatus.FINISHED: queue.finished_job_registry.count,
        JobStatus.FAILED: queue.failed_job_registry.count,
        JobStatus.DEFERRED: queue.deferred_job_registry.count,
        JobStatus.SCHEDULED: queue.scheduled_job_registry.count
    }


def get_jobs_by_queue():
    """Get the current jobs by queue.

    Returns:
        dict: Dictionary of job count by status for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queues = Queue.all()

    return {
        q.name: get_queue_jobs(q.name) for q in queues
    }
