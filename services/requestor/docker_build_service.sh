#/bin/bash
echo 'Building Requestor Service...'
echo "${BLUE_CORE_DOCKER_ORG}/blue-service-requestor${BLUE_BUILD_IMG_SUFFIX}:v${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# build docker
docker buildx build  --platform ${BLUE_BUILD_PLATFORM} ${BLUE_BUILD_CACHE_ARG} --build-arg BLUE_DEPLOY_VERSION --build-arg BLUE_BUILD_CACHE_ARG  --build-arg BLUE_BUILD_LIB_ARG ${BLUE_BUILD_PUBLISH} -t ${BLUE_DEV_DOCKER_ORG}/blue-service-requestor${BLUE_BUILD_IMG_SUFFIX}:v${BLUE_DEPLOY_VERSION} -f Dockerfile.service .

echo 'Done...'
