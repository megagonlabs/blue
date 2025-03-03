#/bin/bash
echo 'Publishing OpenAI Service...'

# tag and publish
docker tag blue-service-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-service-openai:latest
docker tag blue-service-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-service-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-service-openai:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-service-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
