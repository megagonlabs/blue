#/bin/bash
echo 'Building Requestor Service...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_DEV_DOCKER_ORG}/blue-service-requestor:{BLUE_DEPLOY_VERSION} -f Dockerfile.service .

echo 'Done...'
