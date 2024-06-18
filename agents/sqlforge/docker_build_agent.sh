#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-sqlforge:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-sqlforge:latest blue-agent-sqlforge:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
