"""
Tests for the rq_exporter.utils module.

"""

import unittest
from unittest.mock import patch, mock_open, Mock, PropertyMock, call

import rq
from rq.job import JobStatus
from redis.exceptions import RedisError

from rq_exporter.utils import get_redis_connection, get_workers_stats, get_queue_jobs, get_jobs_by_queue


class GetRedisConnectionTestCase(unittest.TestCase):
    """Tests for the `get_redis_connection` function."""

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_from_url(self):
        """When the `url` argument is passed the connection must be created with `Redis.from_url`."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection(url='redis://')

            Redis.from_url.assert_called_with('redis://')

            open.assert_not_called()

            Redis.assert_not_called()

            self.assertEqual(connection, Redis.from_url.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_without_url(self):
        """When the `url` argument is not set the connection must be created from the other options."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection(
                host='redis_host',
                port='6363',
                db='1'
            )

            Redis.from_url.assert_not_called()

            open.assert_not_called()

            Redis.assert_called_with(
                host='redis_host',
                port='6363',
                db='1',
                password=None
            )

            self.assertEqual(connection, Redis.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_sentinel(self):
        """When the `sentinel` argument is set the connection must be created from the sentinel."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1',
                sentinel_port='26379',
                sentinel_master='mymaster'
            )

            Sentinel.assert_called_once_with(
                [('127.0.0.1', '26379')],
                sentinel_kwargs={'password': None, 'socket_timeout': 1}
            )

            Sentinel().master_for.assert_called_once_with(
                'mymaster',
                db='0',
                socket_timeout=1
            )

            open.assert_not_called()

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_sentinel_port_with_hostname(self):
        """The port provided with the hostname argument `sentinel` must be used instead of `sentinel_port`."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1:26380',
            )

            Sentinel.assert_called_once_with(
                [('127.0.0.1', '26380')],
                sentinel_kwargs={'password': None, 'socket_timeout': 1}
            )

            open.assert_not_called()

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_multiple_sentinel_hosts(self):
        """Test passing mutliple Sentinel hosts using the `sentinel` argument."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1,sentinel2,example.com',
            )

            Sentinel.assert_called_once_with(
                [
                    ('127.0.0.1', '26379'),
                    ('sentinel2', '26379'),
                    ('example.com', '26379')
                ],
                sentinel_kwargs={'password': None, 'socket_timeout': 1}
            )

            open.assert_not_called()

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_multiple_sentinel_hosts_and_ports(self):
        """Test passing mutliple Sentinel hosts with different ports using the `sentinel` argument."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1:26380,sentinel2,example.com:26381',
            )

            Sentinel.assert_called_once_with(
                [
                    ('127.0.0.1', '26380'),
                    ('sentinel2', '26379'),  # Default port when not specified
                    ('example.com', '26381')
                ],
                sentinel_kwargs={'password': None, 'socket_timeout': 1}
            )

            open.assert_not_called()

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_sentinel_using_password(self):
        """The `password` must be used with the sentinel connection."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1:26380',
                password='123456'
            )

            Sentinel.assert_called_once_with(
                [('127.0.0.1', '26380')],
                sentinel_kwargs={'password': '123456', 'socket_timeout': 1}
            )

            open.assert_not_called()

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open(read_data=' FILEPASS \n'))
    def test_creating_redis_connection_with_sentinel_using_password_file(self):
        """The password must be set from the `password_file` argument if it was passed."""
        with patch('rq_exporter.utils.Sentinel') as Sentinel:
            connection = get_redis_connection(
                sentinel='127.0.0.1:26380',
                password='123456',
                password_file='/path/to/redis_pass'
            )

            Sentinel.assert_called_once_with(
                [('127.0.0.1', '26380')],
                sentinel_kwargs={'password': 'FILEPASS', 'socket_timeout': 1}
            )

            open.assert_called_with('/path/to/redis_pass', 'r')

            self.assertEqual(connection, Sentinel().master_for.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_password(self):
        """The `password` argument must be used if `password_file` was not passed."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection(
                host='redis_host',
                port='6379',
                db='0',
                password='123456'
            )

            Redis.from_url.assert_not_called()

            open.assert_not_called()

            Redis.assert_called_with(
                host='redis_host',
                port='6379',
                db='0',
                password='123456'
            )

            self.assertEqual(connection, Redis.return_value)

    @patch('builtins.open', mock_open(read_data=' FILEPASS \n'))
    def test_creating_redis_connection_with_password_from_file(self):
        """The password must be set from the `password_file` argument if it was passed."""
        with patch('rq_exporter.utils.Redis') as Redis:
            connection = get_redis_connection(
                host='redis_host',
                port='6379',
                db='0',
                password='123456',
                password_file='/path/to/redis_pass'
            )

            Redis.from_url.assert_not_called()

            open.assert_called_with('/path/to/redis_pass', 'r')

            Redis.assert_called_with(
                host='redis_host',
                port='6379',
                db='0',
                password='FILEPASS'
            )

            self.assertEqual(connection, Redis.return_value)

    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_open_file_raises_IOError(self):
        """An `IOError` exception must be raised if there was error while opening the password file."""
        open.side_effect = IOError('Error opening the file')

        with patch('rq_exporter.utils.Redis') as Redis:

            with self.assertRaises(IOError):
                get_redis_connection(password_file='/path/to/redis_pass')

            Redis.from_url.assert_not_called()

            open.assert_called_with('/path/to/redis_pass', 'r')

            Redis.assert_not_called()


class GetWorkersStatsTestCase(unittest.TestCase):
    """Tests for the `get_workers_stats` function."""

    @patch('rq_exporter.utils.Worker')
    def test_on_redis_errors_raises_RedisError(self, Worker):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        Worker.all.side_effect = RedisError('Connection error')

        with self.assertRaises(RedisError):
            get_workers_stats()

    @patch('rq_exporter.utils.Worker')
    def test_returns_empty_list_without_workers(self, Worker):
        """Without any available workers an empty list must be returned."""
        Worker.all.return_value = []

        workers = get_workers_stats()

        Worker.all.assert_called_once_with()

        self.assertEqual(workers, [])

    @patch('rq_exporter.utils.Worker')
    def test_returns_worker_stats(self, Worker):
        """When there are workers, a list of worker info dicts must be returned."""
        worker_one = Mock()
        worker_one.configure_mock(**{
            'name': 'worker_one',
            'queue_names.return_value': ['default'],
            'get_state.return_value': 'idle',
            'successful_job_count': 1,
            'failed_job_count': 2,
            'total_working_time': 3
        })

        worker_two = Mock()
        worker_two.configure_mock(**{
            'name': 'worker_two',
            'queue_names.return_value': ['high', 'default', 'low'],
            'get_state.return_value': 'busy',
            'successful_job_count': 4,
            'failed_job_count': 5,
            'total_working_time': 6
        })

        Worker.all.return_value = [worker_one, worker_two]

        workers = get_workers_stats()

        Worker.all.assert_called_once_with()

        self.assertEqual(
            workers,
            [
                {
                    'name': 'worker_one',
                    'queues': ['default'],
                    'state': 'idle',
                    'successful_job_count': 1,
                    'failed_job_count': 2,
                    'total_working_time': 3
                },
                {
                    'name': 'worker_two',
                    'queues': ['high', 'default', 'low'],
                    'state': 'busy',
                    'successful_job_count': 4,
                    'failed_job_count': 5,
                    'total_working_time': 6
                }
            ]
        )

    @patch('rq_exporter.utils.Worker')
    def test_passing_custom_Worker_class(self, Worker):
        """Test passing a custom `Worker` class."""
        worker_class = Mock()
        worker_class.all.return_value = []

        get_workers_stats(worker_class)

        Worker.all.assert_not_called()
        worker_class.all.assert_called_once_with()


class GetQueueJobsTestCase(unittest.TestCase):
    """Tests for the `get_queue_jobs` function."""

    @patch('rq_exporter.utils.Queue')
    def test_on_redis_errors_raises_RedisError(self, Queue):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        type(Queue.return_value).count = PropertyMock(
            side_effect=RedisError('Connection error'))

        with self.assertRaises(RedisError):
            get_queue_jobs('queue_name')

        Queue.assert_called_once_with('queue_name')

    @patch('rq_exporter.utils.Queue')
    def test_get_queue_jobs_return_value(self, Queue):
        """On success a dict of jobs count per status must be returned."""
        type(Queue.return_value).count = PropertyMock(return_value=2)
        type(Queue.return_value.started_job_registry).count = PropertyMock(
            return_value=3
        )
        type(Queue.return_value.finished_job_registry).count = PropertyMock(
            return_value=15
        )
        type(Queue.return_value.failed_job_registry).count = PropertyMock(
            return_value=5
        )
        type(Queue.return_value.deferred_job_registry).count = PropertyMock(
            return_value=1
        )
        type(Queue.return_value.scheduled_job_registry).count = PropertyMock(
            return_value=4
        )

        queue_jobs = get_queue_jobs('queue_name')

        Queue.assert_called_once_with('queue_name')

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

    @patch('rq_exporter.utils.Queue')
    def test_passing_custom_Queue_class(self, Queue):
        """Test passing a custom `Queue` class."""
        queue_class = Mock()

        get_queue_jobs('queue_name', queue_class)

        Queue.assert_not_called()
        queue_class.assert_called_once_with('queue_name')


class GetJobsByQueueTestCase(unittest.TestCase):
    """Tests for the `get_jobs_by_queue` function."""

    @patch('rq_exporter.utils.Queue')
    def test_on_redis_errors_raises_RedisError(self, Queue):
        """On Redis connection errors, exceptions subclasses of `RedisError` will be raised."""
        Queue.all.side_effect = RedisError('Connection error')

        with self.assertRaises(RedisError):
            get_jobs_by_queue()

        Queue.all.assert_called_once_with()

    @patch('rq_exporter.utils.Queue')
    def test_return_value_without_any_queues_available(self, Queue):
        """If there are no queues, an empty dict must be returned."""
        Queue.all.return_value = []

        jobs = get_jobs_by_queue()

        Queue.all.assert_called_once_with()
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

        jobs = get_jobs_by_queue()

        Queue.all.assert_called_once_with()

        get_queue_jobs.assert_has_calls(
            # The Queue class is also passed
            [call('default', Queue), call('high', Queue)]
        )

        self.assertEqual(
            jobs,
            {
                'default': q_default_jobs,
                'high': q_high_jobs
            }
        )

    @patch('rq_exporter.utils.Queue')
    def test_passing_custom_Queue_class(self, Queue):
        """Test passing a custom `Queue` class."""
        queue_class = Mock()
        queue_class.all.return_value = []

        get_jobs_by_queue(queue_class)

        Queue.all.assert_not_called()
        queue_class.all.assert_called_once_with()
