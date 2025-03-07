#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_DEV_DOCKER_ORG}/blue-operator-openai:{BLUE_DEPLOY_VERSION} -f Dockerfile.operator .

echo 'Done...'

