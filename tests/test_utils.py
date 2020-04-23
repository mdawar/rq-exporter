"""
Tests for the rq_exporter.utils module.

"""

import unittest
from unittest.mock import patch, mock_open, Mock, PropertyMock, call

import rq
from rq.job import JobStatus
from redis.exceptions import RedisError

from rq_exporter import config
from rq_exporter.utils import get_redis_connection, get_workers_stats, get_queue_jobs, get_jobs_by_queue


class GetRedisConnectionTestCase(unittest.TestCase):
    """Tests for the `get_redis_connection` function."""

    @patch.multiple(
        config,
        REDIS_URL = 'redis://',
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6363',
        REDIS_DB = '1',
        REDIS_PASS = '123456',
        REDIS_PASS_FILE = '/run/secrets/redis_pass'
    )
    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_from_url(self):
        """When `config.REDIS_URL` is set connection must be created with `Redis.from_url`."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection()

            Redis.from_url.assert_called_with('redis://')

            open.assert_not_called()

            Redis.assert_not_called()

            self.assertEqual(connection, Redis.from_url.return_value)

    @patch.multiple(
        config,
        REDIS_URL = None,
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6363',
        REDIS_DB = '1',
        REDIS_PASS = None,
        REDIS_PASS_FILE = None
    )
    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_without_url(self):
        """When `config.REDIS_URL` is not set the connection must be created from the other options."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection()

            Redis.from_url.assert_not_called()

            open.assert_not_called()

            Redis.assert_called_with(
                host = 'redis_host',
                port = '6363',
                db = '1',
                password = None
            )

            self.assertEqual(connection, Redis.return_value)

    @patch.multiple(
        config,
        REDIS_URL = None,
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6379',
        REDIS_DB = '0',
        REDIS_PASS = '123456',
        REDIS_PASS_FILE = None
    )
    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_password(self):
        """The option `config.REDIS_PASS` must be used if `config.REDIS_PASS_FILE` is not set."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection()

            Redis.from_url.assert_not_called()

            open.assert_not_called()

            Redis.assert_called_with(
                host = 'redis_host',
                port = '6379',
                db = '0',
                password = '123456'
            )

            self.assertEqual(connection, Redis.return_value)

    @patch.multiple(
        config,
        REDIS_URL = None,
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6379',
        REDIS_DB = '0',
        REDIS_PASS = '123456',
        REDIS_PASS_FILE = '/path/to/redis_pass'
    )
    @patch('builtins.open', mock_open(read_data=' FILEPASS \n'))
    def test_creating_redis_connection_with_password_from_file(self):
        """The option `config.REDIS_PASS_FILE` must be used if set."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection()

            Redis.from_url.assert_not_called()

            open.assert_called_with('/path/to/redis_pass', 'r')

            Redis.assert_called_with(
                host = 'redis_host',
                port = '6379',
                db = '0',
                password = 'FILEPASS'
            )

            self.assertEqual(connection, Redis.return_value)

    @patch.multiple(
        config,
        REDIS_URL = None,
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6379',
        REDIS_DB = '0',
        REDIS_PASS = '123456',
        REDIS_PASS_FILE = '/path/to/redis_pass'
    )
    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_open_file_raises_IOError(self):
        """An `IOError` exception must be raised if there was error while opening the password file."""
        open.side_effect = IOError('Error opening the file')

        with patch('rq_exporter.utils.Redis') as Redis:

            with self.assertRaises(IOError):
                get_redis_connection()

            Redis.from_url.assert_not_called()

            open.assert_called_with('/path/to/redis_pass', 'r')

            Redis.assert_not_called()


class GetWorkersStatsTestCase(unittest.TestCase):
    """Tests for the `get_workers_stats` function."""

    @patch('rq_exporter.utils.Worker')
    def test_on_redis_errors_raises_RedisError(self, Worker):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        Worker.all.side_effect = RedisError('Connection error')

        connection = Mock()

        with self.assertRaises(RedisError):
            get_workers_stats(connection)

        Worker.all.assert_called_with(connection=connection)

    @patch('rq_exporter.utils.Worker')
    def test_returns_empty_list_without_workers(self, Worker):
        """Without any available workers an empty list must be returned."""
        Worker.all.return_value = []

        connection = Mock()

        workers = get_workers_stats(connection)

        Worker.all.assert_called_with(connection=connection)

        self.assertEqual(workers, [])

    @patch('rq_exporter.utils.Worker')
    def test_returns_worker_stats(self, Worker):
        """When there are workers, a list of worker info dicts must be returned."""
        q_default = Mock()
        q_default.configure_mock(name='default')

        q_high = Mock()
        q_high.configure_mock(name='high')

        q_low = Mock()
        q_low.configure_mock(name='low')

        worker_one = Mock()
        worker_one.configure_mock(**{
            'name': 'worker_one',
            'queues': [q_default],
            'get_state.return_value': 'idle'
        })

        worker_two = Mock()
        worker_two.configure_mock(**{
            'name': 'worker_two',
            'queues': [q_high, q_default, q_low],
            'get_state.return_value': 'busy'
        })

        Worker.all.return_value = [worker_one, worker_two]

        connection = Mock()

        workers = get_workers_stats(connection)

        Worker.all.assert_called_with(connection=connection)

        self.assertEqual(
            workers,
            [
                {
                    'name': 'worker_one',
                    'queues': ['default'],
                    'state': 'idle'
                },
                {
                    'name': 'worker_two',
                    'queues': ['high', 'default', 'low'],
                    'state': 'busy'
                }
            ]
        )


class GetQueueJobsTestCase(unittest.TestCase):
    """Tests for the `get_queue_jobs` function."""

    @patch('rq_exporter.utils.Queue')
    def test_on_redis_errors_raises_RedisError(self, Queue):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        type(Queue.return_value).count = PropertyMock(side_effect=RedisError('Connection error'))

        connection = Mock()

        with self.assertRaises(RedisError):
            get_queue_jobs('queue_name', connection)

        Queue.assert_called_with('queue_name', connection=connection)

    @patch('rq_exporter.utils.Queue')
    def test_get_queue_jobs_return_value(self, Queue):
        """On success a dict of jobs count per status must be returned."""
        type(Queue.return_value).count = PropertyMock(return_value=2)
        type(Queue.return_value.started_job_registry).count = PropertyMock(return_value=3)
        type(Queue.return_value.finished_job_registry).count = PropertyMock(return_value=15)
        type(Queue.return_value.failed_job_registry).count = PropertyMock(return_value=5)
        type(Queue.return_value.deferred_job_registry).count = PropertyMock(return_value=1)
        type(Queue.return_value.scheduled_job_registry).count = PropertyMock(return_value=4)

        queue_jobs = get_queue_jobs('queue_name')

        Queue.assert_called_with('queue_name', connection=None)

        self.assertEqual(
            queue_jobs,
            {
                JobStatus.QUEUED: 2,
                JobStatus.STARTED: 3,
                JobStatus.FINISHED: 15,
                JobStatus.FAILED: 5,
                JobStatus.DEFERRED: 1,
                JobStatus.SCHEDULED: 4
            }
        )


class GetJobsByQueueTestCase(unittest.TestCase):
    """Tests for the `get_jobs_by_queue` function."""

    @patch('rq_exporter.utils.Queue')
    def test_on_redis_errors_raises_RedisError(self, Queue):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        Queue.all.side_effect = RedisError('Connection error')

        connection = Mock()

        with self.assertRaises(RedisError):
            get_jobs_by_queue(connection)

        Queue.all.assert_called_with(connection=connection)

    @patch('rq_exporter.utils.Queue')
    def test_return_value_without_any_queues_available(self, Queue):
        """If there are no queues, an empty dict must be returned."""
        Queue.all.return_value = []

        jobs = get_jobs_by_queue()

        Queue.all.assert_called_with(connection=None)
        self.assertEqual(jobs, {})

    @patch('rq_exporter.utils.get_queue_jobs')
    @patch('rq_exporter.utils.Queue')
    def test_return_value_with_queues_available(self, Queue, get_queue_jobs):
        """On success a dict of the queue names and their jobs dicts must be returned."""
        q_default = Mock()
        q_default.configure_mock(name='default')
        q_default_jobs = {
            JobStatus.QUEUED: 2,
            JobStatus.STARTED: 3,
            JobStatus.FINISHED: 15,
            JobStatus.FAILED: 5,
            JobStatus.DEFERRED: 1,
            JobStatus.SCHEDULED: 4
        }

        q_high = Mock()
        q_high.configure_mock(name='high')
        q_high_jobs = {
            JobStatus.QUEUED: 10,
            JobStatus.STARTED: 4,
            JobStatus.FINISHED: 25,
            JobStatus.FAILED: 22,
            JobStatus.DEFERRED: 5,
            JobStatus.SCHEDULED: 1
        }

        Queue.all.return_value = [q_default, q_high]


        get_queue_jobs.side_effect = [q_default_jobs, q_high_jobs]

        connection = Mock()

        jobs = get_jobs_by_queue(connection)

        Queue.all.assert_called_with(connection=connection)

        get_queue_jobs.assert_has_calls([
            call('default', connection),
            call('high', connection)
        ])

        self.assertEqual(
            jobs,
            {
                'default': q_default_jobs,
                'high': q_high_jobs
            }
        )
