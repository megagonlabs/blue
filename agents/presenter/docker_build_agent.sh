#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-presenter:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-presenter:latest blue-agent-presenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
