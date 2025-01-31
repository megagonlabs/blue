#/bin/bash
echo 'Building docker image...'

# build docker
docker build -t blue-agent-visualizer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-visualizer:latest blue-agent-visualizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
