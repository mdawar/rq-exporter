"""
RQ exporter utility functions.

"""

import logging
from redis import Redis
from redis.sentinel import Sentinel
from rq import Queue, Worker
from rq.job import JobStatus, Job


logger = logging.getLogger(__name__)


def get_redis_connection(host='localhost', port='6379', db='0', sentinel=None,
                         sentinel_port='26379', sentinel_master=None,
                         password=None, password_file=None, url=None,
                         ssl=False, ssl_cert_reqs=None):
    """Get the Redis connection instance.

    Note:
        If the `url` is provided, all the other options are ignored.
        If `password_file` is provided it will be used instead of `password.`

    Args:
        host (str): Redis hostname
        port (str, int): Redis server port number
        db (str, int): Redis database number
        sentinel (str): Redis sentinel
        sentinel_port (str, int): Redis sentinel port number
        sentinel_master (str): Redis sentinel master name
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

    if sentinel:
        addr_list = [
            (
                url.split(':')[0],
                url.split(':')[1] if ':' in url else sentinel_port
            )
            for url in sentinel.split(",")
        ]

        return Sentinel(
            addr_list,
            sentinel_kwargs={'password': password, 'socket_timeout': 1}
        ).master_for(sentinel_master, password=password, db=db, socket_timeout=1)

    return Redis(host=host, port=port, db=db, password=password, ssl=ssl, ssl_cert_reqs=ssl_cert_reqs)


def get_workers_stats(connection, worker_class=None):
    """Get the RQ workers stats.

    Args:
        connection (redis.Redis): Redis connection instance.
        worker_class (type): RQ Worker class

    Returns:
        list: List of worker stats as a dict {name, queues, state}

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    worker_class = worker_class if worker_class is not None else Worker

    workers = worker_class.all(connection)

    return [
        {
            'name': w.name,
            'queues': w.queue_names(),
            'state': w.get_state(),
            'successful_job_count': w.successful_job_count,
            'failed_job_count': w.failed_job_count,
            'total_working_time': w.total_working_time
        }
        for w in workers
    ]


def get_queue_jobs(connection, queue_name, queue_class=None):
    """Get the jobs by status of a Queue.

    Args:
        connection (redis.Redis): Redis connection instance.
        queue_name (str): The RQ Queue name
        queue_class (type): RQ Queue class

    Returns:
        dict: Number of jobs by job status

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue_class = queue_class if queue_class is not None else Queue

    queue = queue_class(connection=connection, name=queue_name)

    return {
        JobStatus.QUEUED: queue.count,
        JobStatus.STARTED: queue.started_job_registry.count,
        JobStatus.FINISHED: queue.finished_job_registry.count,
        JobStatus.FAILED: queue.failed_job_registry.count,
        JobStatus.DEFERRED: queue.deferred_job_registry.count,
        JobStatus.SCHEDULED: queue.scheduled_job_registry.count
    }


def get_jobs_by_queue(connection, queue_class=None):
    """Get the current jobs by queue.

    Args:
        connection (redis.Redis): Redis connection instance.
        queue_class (type): RQ Queue class

    Returns:
        dict: Dictionary of job count by status for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue_class = queue_class if queue_class is not None else Queue

    queues = queue_class.all(connection)

    return {
        q.name: get_queue_jobs(connection, q.name, queue_class) for q in queues
    }


def get_finished_jobs(connection, queue_class=None) -> list[Job]:
    """Get the current jobs by queue.

    Args:
        connection (redis.Redis): Redis connection instance.
        queue_class (type): RQ Queue class

    Returns:
        dict: List of Jobs with details for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors
    """
    queue_class = queue_class if queue_class is not None else Queue

    queues = queue_class.all(connection)
    jobs = []
    logger.debug("Found {} queues".format(len(queues)))
    for q in queues:
        finished_registry = q.finished_job_registry
        finished_job_ids = finished_registry.get_job_ids()
        logger.debug("Queue {} has {} finished jobs".format(q.name, len(finished_job_ids)))
        for job_id in finished_job_ids:
            job = q.fetch_job(job_id)
            if job:
                jobs.append(job)
    return jobs
