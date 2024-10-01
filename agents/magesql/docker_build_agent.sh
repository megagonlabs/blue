#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-magesql:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-magesql:latest blue-agent-magesql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
