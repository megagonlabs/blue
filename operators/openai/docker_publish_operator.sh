#/bin/bash
echo 'Publishing OpenAI Operator...'

# tag and publish
docker tag blue-operator-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-operator-openai:latest
docker tag blue-operator-openai:latest ${BLUE_DEV_DOCKER_ORG}/blue-operator-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-operator-openai:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-operator-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
