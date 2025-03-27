#/bin/bash
echo 'Building OpenAI Service...'
echo "${BLUE_CORE_DOCKER_ORG}/blue-service-openai:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_DEV_DOCKER_ORG}/blue-service-openai:${BLUE_DEPLOY_VERSION} -f Dockerfile.service .

echo 'Done...'
