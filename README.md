# Python RQ Prometheus Exporter

[![PyPI](https://img.shields.io/pypi/v/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/rq-exporter)](https://libraries.io/pypi/rq-exporter)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/mdawar/rq-exporter?sort=semver)](https://hub.docker.com/r/mdawar/rq-exporter)

Prometheus metrics exporter Python RQ (Redis Queue) job queue library.

## Installation

Install the Python package:

```console
$ pip install rq-exporter
```

## Starting the Server

```console
$ # Run the exporter on port 8000
$ rq-exporter
$ # Run the exporter on a different port
$ rq-exporter 8080
```

## Docker Image

This exporter is available as a [Docker image](https://hub.docker.com/r/mdawar/rq-exporter):

```console
$ # Pull the latest image
$ docker pull mdawar/rq-exporter
$ # Pull a specific version
$ docker pull mdawar/rq-exporter:v1.0.0
```

The released versions are available as [Docker image tags](https://hub.docker.com/r/mdawar/rq-exporter/tags).

Usage:

```console
$ # Run the exporter and publish the port 8000 on the host
$ docker run -it -p 8000:8000 rq-exporter
$ # Use the -d option to run the container in the background (detached)
$ docker run -d -p 8000:8000 rq-exporter
$ # Override Gunicorn command line options
$ # All the command line arguments will be passed to gunicorn
$ docker run -it -p 8080:8080 rq-exporter -b 0.0.0.0:8080 --log-level debug --threads 2
$ # Set environment variables using -e
$ docker run -it -p 8000:8000 -e RQ_REDIS_HOST=redis -e RQ_REDIS_PASS=123456 rq-exporter
```

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

* `rq_jobs`: RQ jobs by queue and status

    * **Type**: Gauge
    * **Labels**: `queue`, `status`

    Example:

    ```
    rq_jobs{queue="default", status="queued"} 2.0
    rq_jobs{queue="default", status="started"} 1.0
    rq_jobs{queue="default", status="finished"} 5.0
    rq_jobs{queue="default", status="failed"} 1.0
    rq_jobs{queue="default", status="deferred"} 1.0
    rq_jobs{queue="default", status="scheduled"} 2.0
    ```

**Request processing metrics:**

* `rq_request_processing_seconds_count`: Number of requests processed

    * **Type**: Summary

* `rq_request_processing_seconds_sum`: Total sum of time in seconds processing the requests

    * **Type**: Summary

* `rq_request_processing_seconds_created`: Time created at (`time.time()` return value)

    * **Type**: Gauge

## Configuration

Environment variables:

`RQ_REDIS_URL`: Redis URL in the form `redis://:[password]@[host]:[port]/[db]`

Or you can use these variables instead:

* `RQ_REDIS_HOST`: Redis host name (default: `localhost`)
* `RQ_REDIS_PORT`: Redis port number (default: `6379`)
* `RQ_REDIS_DB`: Redis database number (default: `0`)
* `RQ_REDIS_PASS`: Redis password (default: `None`)
* `RQ_REDIS_PASS_FILE`: Redis password file (e.g. Path of a mounted Docker secret)

**Note**: When `RQ_REDIS_PASS_FILE` is set `RQ_REDIS_PASS` will be ignored.

`RQ_EXPORTER_LOG_LEVEL`: Logging level (default: `INFO`), only used when executing the package `python -m rq_exporter`

When using **Gunicorn** the level will be set from its logger, you can pass the logging level using the `--log-level` option.

## Using With Gunicorn

The WSGI application can be created using the `rq_exporter.create_app()` function:

```console
$ gunicorn "rq_exporter:create_app()" -b 0.0.0.0:8000 --log-level info
```

**Note about concurrency**:

The exporter is going to work without any problems with multiple workers but you will get different values for these metrics:

* `rq_request_processing_seconds_count`
* `rq_request_processing_seconds_sum`
* `rq_request_processing_seconds_created`

This is fine if you don't care about these metrics, these are only for measuring the count and time processing the RQ data, so the other RQ metrics are not going to be affected.

But you can still use multiple threads with 1 worker process to handle multiple concurrent requests:

```console
$ gunicorn "rq_exporter:create_app()" -b 0.0.0.0:8000 --threads 2
```

## Building the Docker Image

```console
$ # Build the docker image and tag it rq-exporter:latest
$ docker build -t rq-exporter .
```

The image can also be built using `docker-compose`:

```console
$ docker-compose build
```

Check out the `docker-compose.yml` file for usage example.

## Development

```console
$ # Create a new virtualenv
$ python -m venv /path/to/env
$ # Activate the environment
$ source /path/to/env/bin/activate
$ # Install the requirements
$ pip install -r requirements.txt
$ # Run the exporter on port 8000
$ python -m rq_exporter
$ # Run the exporter on a different port
$ python -m rq_exporter 8080
```

## Running the Tests

```console
$ python -m unittest
```

## Contributing

1. Fork the repository
2. Clone the forked repository `git clone <URL>`
3. Create a new feature branch `git checkout -b <BRANCH_NAME>`
4. Make changes and add tests if needed and commit your changes `git commit -am "Your commit message"`
5. Push the new branch to Github `git push origin <BRANCH_NAME>`
6. Create a pull request
