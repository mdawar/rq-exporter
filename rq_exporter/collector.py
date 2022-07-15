"""
RQ metrics collector.

"""

import logging

from rq import Connection
from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from .utils import get_workers_stats, get_jobs_by_queue

logger = logging.getLogger(__name__)


class RQCollector(object):
    """RQ stats collector.

    Args:
        connection (redis.Redis): Redis connection instance.
        worker_class (type): RQ Worker class
        queue_class (type): RQ Queue class

    """

    def __init__(self, connection=None, worker_class=None, queue_class=None):
        self.connection = connection
        self.worker_class = worker_class
        self.queue_class = queue_class

        # RQ data collection count and time in seconds
        self.summary = Summary('rq_request_processing_seconds', 'Time spent collecting RQ data')

    def collect(self):
        """Collect RQ Metrics.

        Note:
            This method will be called on registration and every time the metrics are requested.

        Yields:
            RQ metrics for workers and jobs.

        Raises:
            redis.exceptions.RedisError: On Redis connection errors

        """
        logger.debug('Collecting the RQ metrics...')

        with self.summary.time():
            with Connection(self.connection):
                rq_workers = GaugeMetricFamily('rq_workers', 'RQ workers', labels=['name', 'state', 'queues'])
                rq_workers_success = CounterMetricFamily('rq_workers_success', 'RQ workers success count', labels=['name', 'queues'])
                rq_workers_failed = CounterMetricFamily('rq_workers_failed', 'RQ workers fail count', labels=['name', 'queues'])
                rq_workers_working_time = CounterMetricFamily('rq_workers_working_time', 'RQ workers spent seconds', labels=['name', 'queues'])

                rq_jobs = GaugeMetricFamily('rq_jobs', 'RQ jobs by state', labels=['queue', 'status'])

                workers = get_workers_stats(self.worker_class)
                for worker in workers:
                    label_queues = ','.join(worker['queues'])
                    rq_workers.add_metric([worker['name'], worker['state'], label_queues], 1)
                    rq_workers_success.add_metric([worker['name'], label_queues], worker['successful_job_count'])
                    rq_workers_failed.add_metric([worker['name'], label_queues], worker['failed_job_count'])
                    rq_workers_working_time.add_metric([worker['name'], label_queues], worker['total_working_time'])

                yield rq_workers
                yield rq_workers_success
                yield rq_workers_failed
                yield rq_workers_working_time

                for (queue_name, jobs) in get_jobs_by_queue(self.queue_class).items():
                    for (status, count) in jobs.items():
                        rq_jobs.add_metric([queue_name, status], count)

                yield rq_jobs

        logger.debug('RQ metrics collection finished')
