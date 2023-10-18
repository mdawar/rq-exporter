test:
	safety check
	python -m unittest

build:
	docker build -t rq-exporter .

dev:
	docker compose up

clean:
	docker compose down -v

.PHONY: test build dev clean
