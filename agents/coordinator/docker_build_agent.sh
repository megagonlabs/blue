#/bin/bash
# source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_DEV_DOCKER_ORG}/blue-agent-coordinator:{BLUE_DEPLOY_VERSION} -f Dockerfile.agent .

echo 'Done...'
