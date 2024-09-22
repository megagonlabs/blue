#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-data_planner:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-data_planner:latest blue-agent-data_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
