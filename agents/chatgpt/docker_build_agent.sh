#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-chatgpt:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-chatgpt:latest blue-agent-chatgpt:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
