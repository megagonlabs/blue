#/bin/bash
echo 'Publishing OpenAI Agent...'

# tag and publish
docker tag blue-agent-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-openai:latest
docker tag blue-agent-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-openai:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
