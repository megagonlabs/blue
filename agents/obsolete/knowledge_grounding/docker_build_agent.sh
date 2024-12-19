#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-knowledge_grounding:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-knowledge_grounding:latest blue-agent-knowledge_grounding:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
