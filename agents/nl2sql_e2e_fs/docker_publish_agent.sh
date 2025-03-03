#/bin/bash
echo 'Publishing NL2SQL_E2E_FS Agent...'

# tag and publish
docker tag blue-agent-nl2sql-e2e-fs:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2sql-e2e-fs:latest
docker tag blue-agent-nl2sql-e2e-fs:latest ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2sql-e2e-fs:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2sql-e2e-fs:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-agent-nl2sql-e2e-fs:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
