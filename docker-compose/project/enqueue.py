"""
Enqueue jobs indefinitely for testing.

"""

import sys
import time
import random
import signal

import jobs
import queues


def main(custom_classes=False):
    if custom_classes:
        print('Using queues with custom RQ classes')
        queues_list = (queues.custom_high, queues.custom_default, queues.custom_low)
    else:
        queues_list = (queues.high, queues.default, queues.low)

    while True:
        # Choose a random job
        job = random.choice((jobs.long_running_job, jobs.process_data))

        # Choose a random queue
        queue = random.choice(queues_list)

        print(f'Enqueuing job "{job.__name__}" on queue "{queue.name}"')

        queue.enqueue_call(job, args=[random.randint(2, 10)])

        time.sleep(random.randint(2, 10))


if __name__ == '__main__':
    def signal_handler(sig, frame):
        print('Exiting...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Use custom RQ Worker, Queue and Job classes
    custom_classes = False

    try:
        custom_classes = sys.argv[1] == 'custom'
    except IndexError:
        pass

    main(custom_classes)
