#/bin/bash
echo 'Publishing Platform Frontend...'

# tag and publish
docker tag blue-platform-frontend:latest ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:latest
docker tag blue-platform-frontend:latest ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:latest
docker push ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
