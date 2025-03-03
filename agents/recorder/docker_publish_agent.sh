#/bin/bash
echo 'Publishing Recorder Agent...'

# tag and publish
docker tag blue-agent-recorder:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-recorder:latest
docker tag blue-agent-recorder:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-recorder:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-recorder:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-recorder:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
