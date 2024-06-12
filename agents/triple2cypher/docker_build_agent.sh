#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-triple2cypher:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-triple2cypher:latest blue-agent-triple2cypher:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
