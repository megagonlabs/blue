#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-template-interactive:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-template-interactive:latest blue-agent-template-interactive:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
