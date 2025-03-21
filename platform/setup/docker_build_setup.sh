#/bin/bash
echo "Building docker image ..."
echo "${BLUE_CORE_DOCKER_ORG}/blue-platform-setup${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# build setup
source $(dirname $0)/build_setup.sh

# build docker
docker buildx build  --platform ${BLUE_BUILD_PLATFORM} ${BLUE_BUILD_CACHE_ARG} --build-arg BLUE_BUILD_CACHE_ARG --build-arg BLUE_BUILD_LIB_ARG --push -t ${BLUE_CORE_DOCKER_ORG}/blue-platform-setup${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION} -f Dockerfile.setup .

echo 'Done...'
