"""
Tests for the rq_exporter.collector module.

"""

import unittest
from unittest.mock import patch, Mock

from rq.job import JobStatus
from prometheus_client import Summary
from prometheus_client.core import CollectorRegistry

from rq_exporter.collector import RQCollector


@patch('rq_exporter.collector.get_jobs_by_queue')
@patch('rq_exporter.collector.get_workers_stats')
class RQCollectorTestCase(unittest.TestCase):
    """Tests for the `RQCollector` class."""

    summary_metric = 'rq_request_processing_seconds'
    workers_metric = 'rq_workers'
    workers_success_metric = 'rq_workers_success_total'
    workers_failed_metric = 'rq_workers_failed_total'
    workers_working_time_metric = 'rq_workers_working_time_total'
    jobs_metric = 'rq_jobs'

    def setUp(self):
        """Prepare for the tests.

        The summary metric used to track the count and time in the `RQCollector.collect` method
        is automatically registered on the global REGISTRY.

        """
        # Create a registry for testing to replace the global REGISTRY
        self.registry = CollectorRegistry(auto_describe=True)

        # Default Summary class arguments values
        default_args = Summary.__init__.__defaults__

        # Create a similar default values tuple and replace the default `registry` argument with a mock
        # Mocking `prometheus_client.metrics.REGISTRY` doesn't work as expected because default arguments
        # are evaluated at definition time
        new_default_args = tuple(self.registry if isinstance(arg, CollectorRegistry) else arg for arg in default_args)

        # Patch the default Summary class arguments
        patch('prometheus_client.metrics.Summary.__init__.__defaults__', new_default_args).start()

        # On cleanup call patch.stopall
        self.addCleanup(patch.stopall)

    def test_multiple_instances_raise_ValueError(self, get_workers_stats, get_jobs_by_queue):
        """Creating multiple instances of `RQCollector` registers duplicate summary metric in the registry."""
        RQCollector()

        with self.assertRaises(ValueError) as error:
            RQCollector()

        self.assertTrue('Duplicated timeseries in CollectorRegistry' in str(error.exception))

    def test_summary_metric(self, get_workers_stats, get_jobs_by_queue):
        """Test the summary metric that tracks the requests count and time."""
        collector = RQCollector()

        # Initial values before calling the `collect` method
        self.assertEqual(0, self.registry.get_sample_value(f'{self.summary_metric}_count'))
        self.assertEqual(0, self.registry.get_sample_value(f'{self.summary_metric}_sum'))

        # The `collect` method is a generator
        # Exhaust the generator to get the recorded samples
        list(collector.collect())

        self.assertEqual(1, self.registry.get_sample_value(f'{self.summary_metric}_count'))
        self.assertTrue(self.registry.get_sample_value(f'{self.summary_metric}_sum') > 0)

    def test_passed_connection_is_used(self, get_workers_stats, get_jobs_by_queue):
        """Test that the connection passed to `RQCollector` is used to get the workers and jobs."""
        get_workers_stats.return_value = []
        get_jobs_by_queue.return_value = {}

        connection = Mock()
        collector = RQCollector(connection)

        with patch('rq_exporter.collector.Connection') as Connection:
            list(collector.collect())

        Connection.assert_called_once_with(connection)
        get_workers_stats.assert_called_once_with(None)
        get_jobs_by_queue.assert_called_once_with(None)

    def test_passed_rq_classes_are_used(self, get_workers_stats, get_jobs_by_queue):
        """Test that the RQ classes passed to `RQCollector` are used to get the workers and jobs."""
        get_workers_stats.return_value = []
        get_jobs_by_queue.return_value = {}

        worker_class = Mock()
        queue_class = Mock()

        collector = RQCollector(worker_class=worker_class, queue_class=queue_class)

        with patch('rq_exporter.collector.Connection') as Connection:
            list(collector.collect())

        get_workers_stats.assert_called_once_with(worker_class)
        get_jobs_by_queue.assert_called_once_with(queue_class)

    def test_metrics_with_empty_data(self, get_workers_stats, get_jobs_by_queue):
        """Test the workers and jobs metrics when there's no data."""
        get_workers_stats.return_value = []
        get_jobs_by_queue.return_value = {}

        self.registry.register(RQCollector())

        self.assertEqual(None, self.registry.get_sample_value(self.workers_metric))
        self.assertEqual(None, self.registry.get_sample_value(self.jobs_metric))

    def test_metrics_with_data(self, get_workers_stats, get_jobs_by_queue):
        """Test the workers and jobs metrics when there is data available."""
        workers = [
            {
                'name': 'worker_one',
                'queues': ['default'],
                'state': 'idle',
                'successful_job_count': 1,
                'failed_job_count': 2,
                'total_working_time': 3,
            },
            {
                'name': 'worker_two',
                'queues': ['high', 'default', 'low'],
                'state': 'busy',
                'successful_job_count': 10,
                'failed_job_count': 11,
                'total_working_time': 12,
            }
        ]

        jobs_by_queue = {
            'default': {
                JobStatus.QUEUED: 2,
                JobStatus.STARTED: 3,
                JobStatus.FINISHED: 15,
                JobStatus.FAILED: 5,
                JobStatus.DEFERRED: 1,
                JobStatus.SCHEDULED: 4
            },
            'high': {
                JobStatus.QUEUED: 10,
                JobStatus.STARTED: 4,
                JobStatus.FINISHED: 25,
                JobStatus.FAILED: 22,
                JobStatus.DEFERRED: 5,
                JobStatus.SCHEDULED: 1
            }
        }

        get_workers_stats.return_value = workers
        get_jobs_by_queue.return_value = jobs_by_queue

        # On registration the `collect` method is called
        self.registry.register(RQCollector())

        get_workers_stats.assert_called_once_with(None)
        get_jobs_by_queue.assert_called_once_with(None)

        for w in workers:
            self.assertEqual(1, self.registry.get_sample_value(
                    self.workers_metric,
                    {
                        'name': w['name'],
                        'state': w['state'],
                        'queues': ','.join(w['queues'])
                    }
                )
            )

            labels = {'name': w['name'], 'queues': ','.join(w['queues'])}
            self.assertEqual(w['successful_job_count'], self.registry.get_sample_value(
                self.workers_success_metric,
                labels
            ))
            self.assertEqual(w['failed_job_count'], self.registry.get_sample_value(
                self.workers_failed_metric,
                labels
            ))
            self.assertEqual(w['total_working_time'], self.registry.get_sample_value(
                self.workers_working_time_metric,
                labels
            ))

        for (queue, jobs) in jobs_by_queue.items():
            for (status, value) in jobs.items():
                self.assertEqual(
                    value,
                    self.registry.get_sample_value(
                        self.jobs_metric,
                        {'queue': queue, 'status': status}
                    )
                )
