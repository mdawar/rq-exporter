"""
Tests for the rq_exporter.utils module.

"""

import unittest
from unittest.mock import patch, mock_open

from redis import Redis

from rq_exporter import config
from rq_exporter.utils import get_redis_connection


class GetRedisConnectionTestCase(unittest.TestCase):
    """Tests for the `get_redis_connection` function."""

    @patch.multiple(
        config,
        REDIS_URL = 'redis://',
        REDIS_HOST = 'redis_host',
        REDIS_PORT = '6363',
        REDIS_DB = '1',
        REDIS_AUTH = '123456',
        REDIS_AUTH_FILE = '/run/secrets/redis_pass'
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
        REDIS_AUTH = None,
        REDIS_AUTH_FILE = None
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
        REDIS_AUTH = '123456',
        REDIS_AUTH_FILE = None
    )
    @patch('builtins.open', mock_open())
    def test_creating_redis_connection_with_password(self):
        """The option `config.REDIS_AUTH` must be used if `config.REDIS_AUTH_FILE` is not set."""
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
        REDIS_AUTH = '123456',
        REDIS_AUTH_FILE = '/path/to/redis_pass'
    )
    @patch('builtins.open', mock_open(read_data=' FILEPASS \n'))
    def test_creating_redis_connection_with_password_from_file(self):
        """The option `config.REDIS_AUTH_FILE` must be used if set."""
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
        REDIS_AUTH = '123456',
        REDIS_AUTH_FILE = '/path/to/redis_pass'
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
