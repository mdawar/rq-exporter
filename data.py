queues = {
    'default': {
        'queued': 2,
        'started': 3,
        'finished': 5,
        'failed': 1,
        'deferred': 0,
        'scheduled': 0
    },
    'download': {
        'queued': 5,
        'started': 6,
        'finished': 10,
        'failed': 3,
        'deferred': 0,
        'scheduled': 0
    },
    'convert': {
        'queued': 4,
        'started': 3,
        'finished': 15,
        'failed': 5,
        'deferred': 0,
        'scheduled': 0
    }
}


workers = [
    {
        'name': 'one',
        'queues': ['default'],
        'state': 'idle',
        'failed_job_count': 2,
        'successful_job_count': 15
    },
    {
        'name': 'two',
        'queues': ['default', 'download', 'convert'],
        'state': 'busy',
        'failed_job_count': 5,
        'successful_job_count': 25
    },
    {
        'name': 'three',
        'queues': ['default', 'download'],
        'state': 'busy',
        'failed_job_count': 7,
        'successful_job_count': 27
    }
]
