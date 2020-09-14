"""
Sample jobs used for testing.

"""

import time
import random


def long_running_job(s=10):
    print(f'long_running_job: sleeping for {s} seconds')
    time.sleep(s)

    return s


def short_running_job(s=10):
    s = s/10
    print(f'long_running_job: sleeping for {s} seconds')
    time.sleep(s)

    return s


def process_data(s=10):
    print(f'process_data: sleeping for {s} seconds')
    time.sleep(s)

    failed = random.choice((True, False))

    if failed:
        raise Exception('Job has failed')

    return random.randint(1, 100)
