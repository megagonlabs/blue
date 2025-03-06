#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-observer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-observer:latest blue-agent-observer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
