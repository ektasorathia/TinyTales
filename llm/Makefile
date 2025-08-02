PYPROJECT_VERSION := $(shell grep -m 1 '^version' pyproject.toml | cut -d '"' -f2)
BUILD_INFO ?= $(shell date -u +"%Y%m%d%H%M")-$(shell git rev-parse --short HEAD)
VERSION := $(PYPROJECT_VERSION)-$(BUILD_INFO)
DOCKER_ORG ?= $(USER)
DOCKER_REPO  ?= hub.tess.io/$(DOCKER_ORG)/fastapi-template
DOCKER_IMAGE ?= $(DOCKER_REPO):$(VERSION)

# Python and testing variables
PYTHON := python3
PYLINT := pylint
PYTHON_FILES := $(shell find . -name "*.py")

.PHONY: all format style build docker clean run docker-push docker-clean print-version

all: style build docker

format:
	@echo "Formatting code style."
	which black || $(PYTHON) -m pip install black
	$(PYTHON) -m black -l 100 $(PYTHON_FILES)

style:
	@echo "Checking code style."
	which black || $(PYTHON) -m pip install black
	$(PYTHON) -m black -l 100 --check $(PYTHON_FILES)

pylint:
	@echo "Running Pylint"
	which $(PYLINT) || $(PYTHON) -m pip install pylint
	@# Run pylint and save both score and output
	$(PYTHON) -m pylint $(PYTHON_FILES) --rcfile pyproject.toml > pylint_output.txt || true
	@# Extract score and ensure it's captured even if pylint returns non-zero
	$(eval PYLINT_SCORE := $(shell grep -o '[0-9]\+\.[0-9]\+' pylint_output.txt | head -1))
	@if [ -z "$(PYLINT_SCORE)" ]; then \
		echo "Failed to extract pylint score. Pylint output:"; \
		cat pylint_output.txt; \
		exit 1; \
	fi
	@echo "Pylint Score: $(PYLINT_SCORE)"
	@rm pylint_output.txt

clean:
	rm -rf __pycache__ .pytest_cache pylint_output.txt

build: clean
	@echo "Building the package."
	pip install -e .

docker:
	@echo "Building Docker image $(DOCKER_IMAGE)"
	docker build --no-cache --platform linux/amd64 -t $(DOCKER_IMAGE) .
	docker tag $(DOCKER_IMAGE) $(DOCKER_REPO):latest

docker-push: docker
	@echo "Pushing Docker image $(DOCKER_IMAGE)"
	docker push $(DOCKER_IMAGE)
	docker push $(DOCKER_REPO):latest

run:
	@echo "Running the application with Uvicorn"
	uvicorn app.main:app --reload

docker-clean:
	@echo "Cleaning Docker images and containers"
	docker rm -f $$(docker ps -aq) || true
	docker rmi -f $$(docker images -q) || true

clean:
	@echo "Cleaning up build artifacts."
	@rm -rf build dist *.egg-info

print-version:
	@echo "Current version: $(VERSION)"
	@echo "Docker image: $(DOCKER_IMAGE)"