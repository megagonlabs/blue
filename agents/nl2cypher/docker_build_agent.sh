#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-nl2cypher:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-nl2cypher:latest blue-agent-nl2cypher:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
