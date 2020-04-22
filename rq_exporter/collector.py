"""
RQ metrics collector.

"""

from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily

from .utils import get_workers_stats, get_jobs_by_queue


class RQCollector(object):
    """RQ stats collector.

    Args:
        connection: Redis connection instance.

    """

    def __init__(self, connection=None):
        self.connection = connection

        # RQ stats processing count and time in seconds
        self.summary = Summary('rq_request_processing_seconds', 'Time spent processing RQ stats')

    def collect(self):
        """Collect RQ Metrics.

        Note:
            This method will be called on registration and every time the metrics are requested.

        Yields:
            RQ metrics for workers and jobs.

        """
        with self.summary.time():
            rq_workers = GaugeMetricFamily('rq_workers', 'RQ workers', labels=['name', 'state', 'queues'])
            rq_jobs = GaugeMetricFamily('rq_jobs', 'RQ jobs by state', labels=['queue', 'status'])

            for worker in get_workers_stats(self.connection):
                rq_workers.add_metric([worker['name'], worker['state'], ','.join(worker['queues'])], 1)

            yield rq_workers

            for (queue_name, jobs) in get_jobs_by_queue(self.connection).items():
                for (status, count) in jobs.items():
                    rq_jobs.add_metric([queue_name, status], count)

            yield rq_jobs
