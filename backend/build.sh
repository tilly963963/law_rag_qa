# build dev image
# docker build -f docker/Dockerfile-dev -t cclee-docqa-backend:dev .

IMAGE_TAG=$(git rev-parse --short HEAD) docker compose -f docker-compose-build.yml build
