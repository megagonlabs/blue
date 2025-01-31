#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-summarizer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-summarizer:latest blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
