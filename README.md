# Python RQ Prometheus Exporter

Prometheus metrics exporter for the RQ (Redis Queue) job queue library.

## Exported Metrics

**RQ Metrics:**

* `rq_workers`: RQ workers

    * **Type**: Gauge
    * **Labels**: `name`, `queues`, `state`

    Example:

    ```
    rq_workers{name="40d33ed9541644d79373765e661b7f38", queues="default", state="idle"} 1.0
    rq_workers{name="fe9a433575e04685a53e4794b2eaeea9", queues="high,default,low", state="busy"} 1.0
    ```

* `rq_jobs`: RQ jobs by queue and state

    * **Type**: Gauge
    * **Labels**: `queue`, `state`

    Example:

    ```
    rq_jobs{queue="default", state="queued"} 2.0
    rq_jobs{queue="default", state="started"} 1.0
    rq_jobs{queue="default", state="finished"} 5.0
    rq_jobs{queue="default", state="failed"} 1.0
    rq_jobs{queue="default", state="deferred"} 1.0
    rq_jobs{queue="default", state="scheduled"} 2.0
    ```

**Request processing metrics:**

* `rq_request_processing_seconds`: Request processing count and sum

    * **Type**: Summary

    Exposes:

    * `rq_request_processing_seconds_count`: Number of requests processed (Scrape counts)
    * `rq_request_processing_seconds_sum`: Total sum of time in seconds processing the requests
    * `rq_request_processing_seconds_created`: Time created at (`time.time()` return value)

## Configuration

Environment variables:

`RQ_REDIS_URL`: Redis URL in the form `redis://:[password]@[host]:[port]/[db]`

Or you can use these variables instead:

* `RQ_REDIS_HOST`: Redis host name (default: `localhost`)
* `RQ_REDIS_PORT`: Redis port number (default: `6379`)
* `RQ_REDIS_DB`: Redis database number (default: `0`)
* `RQ_REDIS_AUTH`: Redis password (default: `''`)
* `RQ_REDIS_AUTH_FILE`: Redis password file (e.g. Path of a mounted Docker secret)

When `RQ_REDIS_AUTH_FILE` is set ``RQ_REDIS_AUTH` will be ignored.

## Starting a WSGI Server

```console
# Start a WSGI server on port 8000
$ python -m rq_exporter
```

To start the server on a different port

```console
$ python -m rq_exporter 8080
```

## Using With Gunicorn

The WSGI application instance is available at `rq_exporter.app`:

```console
$ gunicorn rq_exporter:app -b 0.0.0.0:8000
```

**Note about concurrency**:

The exporter is going to work without any problems with multiple workers but you will get different values for these metrics:

* `rq_request_processing_seconds_count`
* `rq_request_processing_seconds_sum`
* `rq_request_processing_seconds_created`

This is fine if you don't care about these metrics, these are only for measuring the count and time processing the RQ data, so the other RQ metrics are not going to be affected.

But you can still use multiple threads with 1 worker process to handle multiple concurrent requests:

```console
$ gunicorn rq_exporter:app -b 0.0.0.0:8000 --threads 2
```
