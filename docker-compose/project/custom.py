"""
Custom RQ Classes.

"""

from rq import Worker, Queue
from rq.job import Job


class CustomJob(Job):
    redis_job_namespace_prefix = 'rq:custom:job:'


class CustomQueue(Queue):
    redis_queue_namespace_prefix = 'rq:custom:queue:'
    job_class = CustomJob


class CustomWorker(Worker):
    redis_worker_namespace_prefix = 'rq:custom:worker:'
    queue_class = CustomQueue
    job_class = CustomJob
