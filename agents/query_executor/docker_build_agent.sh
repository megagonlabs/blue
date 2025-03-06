#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-query_executor:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-query_executor:latest blue-agent-query_executor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
