#/bin/bash
echo "Building docker image ..."
echo "${BLUE_CORE_DOCKER_ORG}/blue-platform-api:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_CORE_DOCKER_ORG}/blue-platform-api:${BLUE_DEPLOY_VERSION} -f Dockerfile.api .

echo 'Done...'
