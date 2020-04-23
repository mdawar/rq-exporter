# Python RQ Prometheus Exporter

![Docker Image Version (latest semver)](https://img.shields.io/docker/v/mdawar/rq-exporter?sort=semver)
![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/mdawar/rq-exporter?sort=semver)

Prometheus metrics exporter for the RQ (Redis Queue) job queue library.

## Docker Image

This exporter is available as a Docker image:

```console
$ # Pull the latest image
$ docker pull mdawar/rq-exporter
$ # Pull a specific version
$ docker pull mdawar/rq-exporter:v1.0.0
```

All the Git tags are available as [Docker image tags](https://hub.docker.com/r/mdawar/rq-exporter/tags).

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

* `rq_request_processing_seconds_count`: Number of requests processed (Scrape counts)

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
$ # Run the image after the build has completed
$ docker run -it -p 8000:8000 rq-exporter
$ # Override Gunicorn command line options
$ docker run -it -p 8080:8080 rq-exporter -b 0.0.0.0:8080 --log-level debug --threads 2
$ # Provide environment variables
$ docker run -it -p 8000:8000 -e RQ_REDIS_HOST=redis -e RQ_REDIS_PASS=123456 rq-exporter
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
