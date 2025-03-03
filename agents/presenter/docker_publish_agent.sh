#/bin/bash
echo 'Publishing Presenter Agent...'

# tag and publish
docker tag blue-agent-presenter:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-presenter:latest
docker tag blue-agent-presenter:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-presenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-presenter:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-presenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
