.PHONY: build test clean run shell

IMAGE_NAME = python-gost-engine
TAG = latest

build:
	docker build -t $(IMAGE_NAME):$(TAG) .

test:
	docker run --rm $(IMAGE_NAME):$(TAG) python3 /app/tests/test_gost.py
	docker run --rm $(IMAGE_NAME):$(TAG) python3 /app/tests/test_ssl.py

test-mount:
	docker run --rm -v $(PWD)/tests:/app/tests $(IMAGE_NAME):$(TAG) python3 /app/tests/test_gost.py

run:
	docker run --rm -it $(IMAGE_NAME):$(TAG) python3

shell:
	docker run --rm -it $(IMAGE_NAME):$(TAG) sh

example:
	docker run --rm -v $(PWD)/examples:/app/examples $(IMAGE_NAME):$(TAG) python3 /app/examples/basic_usage.py

clean:
	docker rmi $(IMAGE_NAME):$(TAG) || true

help:
	@echo "Available targets:"
	@echo "  build       - Build Docker image"
	@echo "  test        - Run test suite"
	@echo "  test-mount  - Run tests with mounted volume"
	@echo "  run         - Run Python interactive shell"
	@echo "  shell       - Run system shell"
	@echo "  example     - Run basic usage example"
	@echo "  clean       - Remove Docker image"
	@echo "  help        - Show this help message"




