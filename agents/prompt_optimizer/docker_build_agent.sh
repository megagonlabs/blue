#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-prompt_optimizer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-prompt_optimizer:latest blue-agent-prompt_optimizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
