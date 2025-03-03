#/bin/bash
echo 'Publishing Clusterer Agent...'

# tag and publish
docker tag blue-agent-clusterer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-clusterer:latest
docker tag blue-agent-clusterer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-clusterer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-clusterer:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-clusterer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
