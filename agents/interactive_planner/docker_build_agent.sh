#/bin/bash
echo 'Building docker image...'

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache -t blue-agent-interactive_planner:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-interactive_planner:latest blue-agent-interactive_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
