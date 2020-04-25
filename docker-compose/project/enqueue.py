"""
Enqueue jobs indefinitely for testing.

"""

import sys
import time
import random
import signal

import jobs
import queues


def main():
    while True:
        # Choose a random job
        job = random.choice((jobs.long_running_job, jobs.process_data))

        # Choose a random queue
        queue = random.choice((queues.high, queues.default, queues.low))

        print(f'Enqueuing job "{job.__name__}" on queue "{queue.name}"')

        queue.enqueue(job, random.randint(2, 10))

        time.sleep(random.randint(2, 10))


if __name__ == '__main__':
    def signal_handler(sig, frame):
        print('Exiting...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
