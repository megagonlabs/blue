#/bin/bash
echo 'Publishing Summarizer Agent...'

# tag and publish
docker tag blue-agent-summarizer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-summarizer:latest
docker tag blue-agent-summarizer:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-summarizer:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
