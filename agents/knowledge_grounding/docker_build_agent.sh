#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-knowledge_grounding:latest -f Dockerfile.agent .

echo 'Done...'
