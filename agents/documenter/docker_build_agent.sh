#/bin/bash
echo 'Building docker image...'

# build docker
docker build -t blue-agent-documenter:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-documenter:latest blue-agent-documenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
