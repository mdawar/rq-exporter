# Python RQ Prometheus Exporter

[![PyPI](https://img.shields.io/pypi/v/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rq-exporter)](https://pypi.org/project/rq-exporter/)
[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/rq-exporter)](https://libraries.io/pypi/rq-exporter)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/mdawar/rq-exporter?sort=semver)](https://hub.docker.com/r/mdawar/rq-exporter)

Prometheus metrics exporter Python RQ (Redis Queue) job queue library.

[![Grafana dashboard](https://grafana.com/api/dashboards/12196/images/8017/image)](https://grafana.com/grafana/dashboards/12196)

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
$ # Run the exporter on port 9726
$ rq-exporter
$ # You can specify a different port by passing the port number
$ rq-exporter 8080
```

**Docker image**:

```console
$ # Run the exporter and publish the port 9726 on the host
$ docker run -it -p 9726:9726 rq-exporter
$ # Use the -d option to run the container in the background (detached)
$ docker run -d -p 9726:9726 rq-exporter
$ # All the command line arguments will be passed to rq-exporter
$ # So you can change the exporter port
$ docker run -it -p 8080:8080 rq-exporter 8080
$ # To set environment variables use the -e option
$ docker run -it -p 9726:9726 -e RQ_REDIS_HOST=redis -e RQ_REDIS_PASS=123456 rq-exporter
```

## Grafana Dashboard

An example [**Grafana** dashboard](https://grafana.com/grafana/dashboards/12196) is available with the ID `12196` for showcasing this exporter's metrics.

You can also find the [JSON file of the dashboard](https://github.com/mdawar/rq-exporter/tree/master/grafana/rq-dashboard.json) in this repository.

**Note**:

- This is just an example dashboard, feel free to use it as a base for your custom dashboard
- You need to adjust the color thresholds to suit your needs for the job status percentage *singlestat* panels
- Some panels might seem duplicated providing percentages and current values, these are just for showcasing the PromQL queries

## Exported Metrics

**RQ metrics:**

Metric Name | Type | Labels | Description
----------- | ---- | ------ | -----------
`rq_workers` | Gauge | `name`, `queues`, `state` | RQ workers
`rq_jobs` | Gauge | `queue`, `status` | RQ jobs by queue and status

**Request processing metrics:**

Metric Name | Type | Description
----------- | ---- | -----------
`rq_request_processing_seconds_count` | Summary | Number of times the RQ data were collected
`rq_request_processing_seconds_sum` | Summary | Total sum of time spent collecting RQ data
`rq_request_processing_seconds_created` | Gauge | Time created at (`time.time()` return value)

Example:

```bash
# HELP rq_request_processing_seconds Time spent collecting RQ data
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
`RQ_EXPORTER_LOG_FORMAT` | `[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s` | Logging handler format string
`RQ_EXPORTER_LOG_DATEFMT` | `%Y-%m-%d %H:%M:%S` | Logging date/time format string

**Note**:

* When `RQ_REDIS_URL` is set the other Redis options will be ignored
* When `RQ_REDIS_PASS_FILE` is set, `RQ_REDIS_PASS` will be ignored

## Serving with Gunicorn

The WSGI application can be created using the `rq_exporter.create_app()` function:

```console
$ gunicorn "rq_exporter:create_app()" -b 0.0.0.0:9726 --log-level info
```

Example [`Dockerfile`](https://github.com/mdawar/rq-exporter/blob/master/Dockerfile.gunicorn) to create a **Docker** image to serve the application with **Gunicorn**

```dockerfile
FROM mdawar/rq-exporter:latest

USER root

RUN pip install --no-cache-dir gunicorn

USER exporter

ENTRYPOINT ["gunicorn", "rq_exporter:create_app()"]

CMD ["-b", "0.0.0.0:9726", "--threads", "2", "--log-level", "info", "--keep-alive", "3"]
```

**Note about concurrency**:

The exporter is going to work without any problems with multiple workers but you will get different values for these metrics:

* `rq_request_processing_seconds_count`
* `rq_request_processing_seconds_sum`
* `rq_request_processing_seconds_created`

This is fine if you don't care about these metrics, these are only for measuring the count and time processing the RQ data, so the other RQ metrics are not going to be affected.

But you can still use multiple threads with 1 worker process to handle multiple concurrent requests:

```console
$ gunicorn "rq_exporter:create_app()" -b 0.0.0.0:9726 --threads 2
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

To start a full development environment with **RQ** workers, **Prometheus** and **Grafana**:

```console
$ docker-compose up
$ # If you want to start multiple workers use the --compatibility flag
$ # which will make docker-compose read the `deploy` section and start multiple replicas
$ docker-compose --compatibility up
```

You can access the services on these ports on your local machine:

- **RQ exporter**: `9726`
- **Redis**: `6379`
- **RQ Dashboard**: `9181`
- **Prometheus**: `9090`
- **Grafana**: `3000` (Login using `admin:admin`)

You can specify the services that you want to start by their name in the `docker-compose.yml` file:

```console
$ # Example starting only the `rq_exporter` and `redis` services
$ docker-compose up rq_exporter redis
```

To run more workers and enqueue more jobs you can scale the `worker` and `enqueue` services:

```console
$ # Run 5 workers
$ docker-compose up -d --scale worker=5
$ # Enqueue more jobs
$ # Scale the enqueue service and the workers
$ docker-compose up -d --scale worker=5 --scale enqueue=2
```

To cleanup after development:

```console
$ # Use -v to remove volumes
$ docker-compose down -v
```

**Note**: If you don't have `docker-compose` installed follow the [installation](https://docs.docker.com/compose/install/) instructions on the official website.

If you want to use the package manually:

```console
$ # Clone the repository
$ git clone <REPO_URL>
$ # Change to the project directory
$ cd rq-exporter
$ # Create a new virtualenv
$ python -m venv /path/to/env
$ # Activate the environment
$ source /path/to/env/bin/activate
$ # Install the requirements
$ pip install -r requirements.txt
$ # Run the exporter on port 9726
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
