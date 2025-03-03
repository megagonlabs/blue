#/bin/bash
echo 'Publishing Visualizer Agent...'

# tag and publish
docker tag blue-agent-visualizer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-visualizer:latest
docker tag blue-agent-visualizer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-visualizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-visualizer:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-visualizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
