# Python RQ Prometheus Exporter

[![PyPI](https://img.shields.io/pypi/v/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/rq-exporter)](https://libraries.io/pypi/rq-exporter)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/mdawar/rq-exporter?sort=semver)](https://hub.docker.com/r/mdawar/rq-exporter)

Prometheus metrics exporter Python RQ (Redis Queue) job queue library.

## Installation

Install the Python package:

```console
$ # Install the latest version
$ pip install rq-exporter
$ # Or you can install a specific version
$ pip install rq-exporter==1.0.0
```

Or download the [Docker image](https://hub.docker.com/r/mdawar/rq-exporter):

```console
$ # Pull the latest image
$ docker pull mdawar/rq-exporter
$ # Or you can pull a specific version
$ docker pull mdawar/rq-exporter:v1.0.0
```

The releases are available as [Docker image tags](https://hub.docker.com/r/mdawar/rq-exporter/tags).

## Usage

**Python package**:

```console
$ # Run the exporter on port 8000
$ rq-exporter
$ # You can specify a different port by passing the port number
$ rq-exporter 8080
```

**Docker image**:

```console
$ # Run the exporter and publish the port 8000 on the host
$ docker run -it -p 8000:8000 rq-exporter
$ # Use the -d option to run the container in the background (detached)
$ docker run -d -p 8000:8000 rq-exporter
$ # The Docker container by default serves the app using Gunicorn
$ # All the command line arguments will be passed to gunicorn
$ # To override the Gunicorn command line options
$ docker run -it -p 8080:8080 rq-exporter -b 0.0.0.0:8080 --log-level debug --threads 2
$ # To set environment variables use the -e option
$ docker run -it -p 8000:8000 -e RQ_REDIS_HOST=redis -e RQ_REDIS_PASS=123456 rq-exporter
```

If you don't want to serve the application using **Gunicorn**, you can override the entrypoint:

```console
$ # Example of setting the entrypoint to rq-exporter
$ docker run -it -p 8000:8000 --entrypoint rq-exporter rq-exporter
$ # The command line arguments will be passed to rq-exporter
$ docker run -it -p 8080:8080 --entrypoint rq-exporter rq-exporter 8080
```

## Exported Metrics

**RQ metrics:**

Metric Name | Type | Labels | Description
----------- | ---- | ------ | -----------
`rq_workers` | Gauge | `name`, `queues`, `state` | RQ workers
`rq_jobs` | Gauge | `queues`, `status` | RQ jobs by queue and status

**Request processing metrics:**

Metric Name | Type | Description
----------- | ---- | -----------
`rq_request_processing_seconds_count` | Summary | Number of requests processed (RQ data collected)
`rq_request_processing_seconds_sum` | Summary | Total sum of time in seconds processing the requests
`rq_request_processing_seconds_created` | Gauge | Time created at (`time.time()` return value)

Example:

```bash
# HELP rq_request_processing_seconds Time spent processing RQ stats
# TYPE rq_request_processing_seconds summary
rq_request_processing_seconds_count 1.0
rq_request_processing_seconds_sum 0.029244607000009637
# TYPE rq_request_processing_seconds_created gauge
rq_request_processing_seconds_created 1.5878023726039658e+09
# HELP rq_workers RQ workers
# TYPE rq_workers gauge
rq_workers{name="40d33ed9541644d79373765e661b7f38", queues="default", state="idle"} 1.0
rq_workers{name="fe9a433575e04685a53e4794b2eaeea9", queues="high,default,low", state="busy"} 1.0
# HELP rq_jobs RQ jobs by state
# TYPE rq_jobs gauge
rq_jobs{queue="default", status="queued"} 2.0
rq_jobs{queue="default", status="started"} 1.0
rq_jobs{queue="default", status="finished"} 5.0
rq_jobs{queue="default", status="failed"} 1.0
rq_jobs{queue="default", status="deferred"} 1.0
rq_jobs{queue="default", status="scheduled"} 2.0
```

## Configuration

Environment variables:

Variable Name | Default Value | Description
------------- | ------------- | -----------
`RQ_REDIS_URL` | `None` | Redis URL in the form `redis://:[password]@[host]:[port]/[db]`
`RQ_REDIS_HOST` | `localhost` | Redis host name
`RQ_REDIS_PORT` | `6379` | Redis port number
`RQ_REDIS_DB` | `0` | Redis database number
`RQ_REDIS_PASS` | `None` | Redis password
`RQ_REDIS_PASS_FILE` | `None` |  Redis password file path (e.g. Path of a mounted Docker secret)
`RQ_EXPORTER_LOG_LEVEL` | `INFO` | Logging level

**Note**:

* When `RQ_REDIS_URL` is set the other Redis options will be ignored
* When `RQ_REDIS_PASS_FILE` is set, `RQ_REDIS_PASS` will be ignored
* When using **Gunicorn** you need to set the logging level using the `--log-level` option

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
$ # You can specify a different port by passing the port number
$ python -m rq_exporter 8080
```

## Running the Tests

```console
$ python -m unittest
```

## Contributing

1. Fork the [repository](https://github.com/mdawar/rq-exporter)
2. Clone the forked repository `git clone <URL>`
3. Create a new feature branch `git checkout -b <BRANCH_NAME>`
4. Make changes and add tests if needed and commit your changes `git commit -am "Your commit message"`
5. Push the new branch to Github `git push origin <BRANCH_NAME>`
6. Create a pull request
