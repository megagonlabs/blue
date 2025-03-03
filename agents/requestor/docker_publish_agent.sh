#/bin/bash
echo 'Publishing Requestor Agent...'

# tag and publish
docker tag blue-agent-requestor:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-requestor:latest
docker tag blue-agent-requestor:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-requestor:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
