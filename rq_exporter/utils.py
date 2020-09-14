"""
RQ exporter utility functions.

"""

from redis import Redis
from rq import Queue, Worker
from rq.job import JobStatus, Job


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


def get_workers_stats(worker_class=None):
    """Get the RQ workers stats.

    Args:
        worker_class (type): RQ Worker class

    Returns:
        list: List of worker stats as a dict {name, queues, state}

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    worker_class = worker_class if worker_class is not None else Worker

    workers = worker_class.all()

    return [
        {
            'name': w.name,
            'queues': w.queue_names(),
            'state': w.get_state()
        }
        for w in workers
    ]


def get_job_timings(job):
    """

    Returns:
        dict:

    """
    # Runtime should never be -1 unless the job is not from a finished_job_registry
    return {
        'func_name': job.func_name,
        'started_at': job.started_at.timestamp(),
        'ended_at': job.ended_at.timestamp(),
        'runtime': (job.ended_at - job.started_at).total_seconds() if job.ended_at else -1
    }


def get_registry_timings(connection, job_registry, limit=3):
    """Get the timings for jobs in a Registry.

    Args:
        job_registry (rq.BaseRegistry): The RQ Registry instance
        limit (int): The max number of jobs to retrieve

    Returns:
        dict: 

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    job_ids = job_registry.get_job_ids(start=limit*-1, end=-1)
    jobs = Job.fetch_many(job_ids, connection=connection)

    return {
        job.id: get_job_timings(job) for job in jobs
    }


def get_queue_jobs(queue_name, queue_class=None):
    """Get the jobs by status of a Queue.

    Args:
        queue_name (str): The RQ Queue name
        queue_class (type): RQ Queue class

    Returns:
        dict: Number of jobs by job status

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue_class = queue_class if queue_class is not None else Queue

    queue = queue_class(queue_name)

    return {
        JobStatus.QUEUED: queue.count,
        JobStatus.STARTED: queue.started_job_registry.count,
        JobStatus.FINISHED: queue.finished_job_registry.count,
        JobStatus.FAILED: queue.failed_job_registry.count,
        JobStatus.DEFERRED: queue.deferred_job_registry.count,
        JobStatus.SCHEDULED: queue.scheduled_job_registry.count
    }


def get_jobs_by_queue(queue_class=None):
    """Get the current jobs by queue.

    Args:
        queue_class (type): RQ Queue class

    Returns:
        dict: Dictionary of job count by status for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue_class = queue_class if queue_class is not None else Queue

    queues = queue_class.all()

    return {
        q.name: get_queue_jobs(q.name, queue_class) for q in queues
    }


def get_finished_registries_by_queue(connection, queue_class=None):
    """Get finished registries by queue.

    Args:
        connection : this is required to fetch jobs
        queue_class (type): RQ Queue class

    Returns:
        dict: Dictionary of job count by status for each queue

    Raises:
        redis.exceptions.RedisError: On Redis connection errors

    """
    queue_class = queue_class if queue_class is not None else Queue

    queues = queue_class.all()

    return {
        q.name: get_registry_timings(connection, q.finished_job_registry) for q in queues
    }