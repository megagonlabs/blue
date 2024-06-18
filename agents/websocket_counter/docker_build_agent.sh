#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-websocket_counter:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-websocker_counter:latest blue-agent-websocker_counter:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
