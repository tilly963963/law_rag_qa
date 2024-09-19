# IMAGE_TAG=dev docker compose -f docker-compose-build.yml build

IMAGE_TAG=$(git rev-parse --short HEAD) docker compose -f docker-compose-build.yml build
