#/bin/bash
echo 'Publishing Platform API...'

# tag and publish
docker tag blue-platform-api:latest ${BLUE_CORE_DOCKER_ORG}/blue-platform-api:latest
docker tag blue-platform-api:latest ${BLUE_CORE_DOCKER_ORG}/blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_CORE_DOCKER_ORG}/blue-platform-api:latest
docker push ${BLUE_CORE_DOCKER_ORG}/blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
