VERSION = $(shell git rev-parse --short HEAD)
UPDATED_DATE := $(shell git log -1 --format=%cd --date=format:%Y%m%d)
UPDATED_TIME := $(shell git log -1 --format=%cd --date=format:%H%M)

DOCKER = IMAGE_TAG=$(VERSION)-$(UPDATED_DATE)-$(UPDATED_TIME) docker compose -f docker-compose-build.yml
RUN_DOCKER = docker-compose -f docker-compose.yml

.PHONY: build down run

build:
	$(DOCKER) build

down:
	$(DOCKER) down

run:
	$(RUN_DOCKER) up --force-recreate -d
