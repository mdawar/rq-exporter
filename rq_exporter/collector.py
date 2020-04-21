from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily
from rq import Queue, Worker
from rq.job import JobStatus
from redis import Redis


class RQCollector(object):
    """RQ stats collector."""

    def __init__(self, connection=None):
        self.redis = connection or Redis()

        # RQ stats processing count and time in seconds
        self.summary = Summary('rq_request_processing_seconds', 'Time spent processing RQ stats')

    def get_queue_jobs(self, queue_name):
        """Get the jobs by state of a Queue.

        :param str, Queue queue_name: The RQ Queue instance or name
        :returns: Dictionary of the number of jobs by state
        :rtype: dict

        """
        if isinstance(queue_name, Queue):
            queue_name = queue_name.name

        queue = Queue(queue_name, connection=self.redis)

        return {
            JobStatus.QUEUED: queue.count,
            JobStatus.STARTED: queue.started_job_registry.count,
            JobStatus.FINISHED: queue.finished_job_registry.count,
            JobStatus.FAILED: queue.failed_job_registry.count,
            JobStatus.DEFERRED: queue.deferred_job_registry.count,
            JobStatus.SCHEDULED: queue.scheduled_job_registry.count
        }

    def get_workers_stats(self):
        """Get the RQ workers stats.

        :returns: List of worker stats
        :rtype: list

        """
        workers = Worker.all(connection=self.redis)

        return [
            {
                'name': w.name,
                'queues': [q.name for q in w.queues],
                'state': w.get_state()
            }
            for w in workers
        ]

    def get_jobs_by_queue(self):
        """Get the current jobs by queue.

        :returns: Dictionary of job count by state for each queue
        :rtype: dict

        """
        queues = Queue.all(connection=self.redis)

        return {
            queue.name: self.get_queue_jobs(queue) for queue in queues
        }

    def collect(self):
        """Yield the RQ metrics.

        This method will be called on registration and every time the metrics are requested.

        """
        with self.summary.time():
            rq_workers = GaugeMetricFamily('rq_workers', 'RQ workers', labels=['name', 'state', 'queues'])
            rq_jobs = GaugeMetricFamily('rq_jobs', 'RQ jobs by state', labels=['queue', 'state'])

            for worker in self.get_workers_stats():
                rq_workers.add_metric([worker['name'], worker['state'], ','.join(worker['queues'])], 1)

            yield rq_workers

            for (queue_name, jobs) in self.get_jobs_by_queue().items():
                for (state, count) in jobs.items():
                    rq_jobs.add_metric([queue_name, state], count)

            yield rq_jobs
