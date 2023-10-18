FROM python:3.11-slim-bookworm

# Create a user and a group
RUN groupadd -g 999 -r exporter && useradd -r -g exporter exporter -u 999

# Create the /app directory and set the owner
RUN mkdir /app \
    && chown -R exporter:exporter /app

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the build context (defined in .dockerignore)
COPY . /app

# Copy the patched files
COPY /rq_exporter/patch/. /usr/local/lib/python3.11/site-packages/rq

USER 999

ENTRYPOINT ["python", "-m", "rq_exporter"]
