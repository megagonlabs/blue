#/bin/bash
echo 'Publishing NL2CYPHER_E2E Agent...'

# tag and publish
docker tag blue-agent-nl2cypher-e2e:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2cypher-e2e:latest
docker tag blue-agent-nl2cypher-e2e:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2cypher-e2e:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2cypher-e2e:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2cypher-e2e:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
