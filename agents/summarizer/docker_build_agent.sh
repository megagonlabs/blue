#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-summarizer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-summarizer:latest blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
