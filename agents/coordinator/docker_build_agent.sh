#/bin/bash
# source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-coordinator:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-coordinator:latest blue-agent-coordinator:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
