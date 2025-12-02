.PHONY: build test clean help

IMAGE_NAME = python-gost-engine
TAG = latest

GOST_HTTP_VERSION ?= 0.1.0

PYTHON_VERSION ?= 3.12

build:
	@echo "Building Docker image $(IMAGE_NAME):$(TAG)..."
	@echo "GOST HTTP version: $(GOST_HTTP_VERSION)"
	@echo "Python version: $(PYTHON_VERSION)"
	docker build \
		-t $(IMAGE_NAME):$(TAG) .
	@echo ""
	@echo "=========================================="
	@echo "Build completed successfully!"
	@echo "=========================================="

test:
	@echo "Running gost_http tests..."
	docker run --rm -v "$(PWD)/tests:/app/tests" $(IMAGE_NAME):$(TAG) python3 /app/tests/test_gost_http.py

clean:
	@echo "Removing Docker image $(IMAGE_NAME):$(TAG)..."
	@docker rmi $(IMAGE_NAME):$(TAG) || true
	@echo "Clean completed."

help:
	@echo "Available targets:"
	@echo "  build  - Build Docker image"
	@echo "  test   - Run gost_http test suite"
	@echo "  clean  - Remove Docker image"
	@echo "  help   - Show this help message"




