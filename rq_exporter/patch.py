from rq.worker import Worker
from rq import get_current_connection


# from .rq.worker
def find_by_key_patched(
    cls,
    worker_key: str,
    connection=None,
    job_class=None,
    queue_class=None,
    serializer=None
):
    prefix = cls.redis_worker_namespace_prefix
    if not worker_key.startswith(prefix):
        raise ValueError('Not a valid RQ worker key: %s' % worker_key)

    if connection is None:
        connection = get_current_connection()

    name = worker_key[len(prefix):]
    worker = cls(
        [],
        name,
        connection=connection,
        job_class=job_class,
        queue_class=queue_class,
        prepare_for_work=False,
        serializer=serializer,
    )

    worker.refresh()
    return worker


# Apply the monkey patch to the Worker class
Worker.find_by_key = classmethod(find_by_key_patched)
