#/bin/bash
echo 'Building OpenAI Service...'
echo "${BLUE_CORE_DOCKER_ORG}/blue-service-openai${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# build docker
docker buildx build  --platform ${BLUE_BUILD_PLATFORM} ${BLUE_BUILD_CACHE_ARG} --build-arg BLUE_BUILD_CACHE_ARG --build-arg BLUE_BUILD_LIB_ARG --push -t ${BLUE_DEV_DOCKER_ORG}/blue-service-openai${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION} -f Dockerfile.service .

echo 'Done...'
