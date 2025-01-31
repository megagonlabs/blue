#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-template:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-template:latest blue-agent-template:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
