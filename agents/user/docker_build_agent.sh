#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-user:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-user:latest blue-agent-user:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
