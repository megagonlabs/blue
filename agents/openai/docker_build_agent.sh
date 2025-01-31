#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-openai:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-openai:latest blue-agent-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
