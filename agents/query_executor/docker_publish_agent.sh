#/bin/bash
echo 'Publishing QueryExecutor Agent...'

# tag and publish
docker tag blue-agent-query_executor:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-query_executor:latest
docker tag blue-agent-query_executor:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-query_executor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-query_executor:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-query_executor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
