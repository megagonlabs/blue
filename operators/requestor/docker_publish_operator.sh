#/bin/bash
echo 'Publishing API Operator...'

# tag and publish
docker tag blue-operator-api:latest ${BLUE_DEV_DOCKER_ORG}/blue-operator-api:latest
docker tag blue-operator-api:latest ${BLUE_DEV_DOCKER_ORG}/blue-operator-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push ${BLUE_DEV_DOCKER_ORG}/blue-operator-api:latest
docker push ${BLUE_DEV_DOCKER_ORG}/blue-operator-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
