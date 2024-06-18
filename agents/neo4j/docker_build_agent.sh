#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-neo4j:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-neo4j:latest blue-agent-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
