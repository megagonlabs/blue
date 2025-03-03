#/bin/bash
echo 'Publishing Observer Agent...'

# tag and publish
docker tag blue-agent-observer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-observer:latest
docker tag blue-agent-observer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-observer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-observer:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-observer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
