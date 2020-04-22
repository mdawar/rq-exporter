"""
Python RQ Prometheus Exporter.

"""

import logging


logger = logging.getLogger(__name__)


gunicorn_logger = logging.getLogger('gunicorn.error')

if gunicorn_logger.hasHandlers():
    # Set the same Gunicorn handlers and logging level
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)


from .exporter import register_collector, create_app
