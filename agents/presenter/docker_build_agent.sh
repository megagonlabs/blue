#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_DEV_DOCKER_ORG}/blue-agent-presenter:{BLUE_DEPLOY_VERSION} -f Dockerfile.agent .

echo 'Done...'
