#/bin/bash
echo 'Publishing Documenter Agent...'

# tag and publish
docker tag blue-agent-documenter:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-documenter:latest
docker tag blue-agent-documenter:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-documenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-documenter:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-documenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
