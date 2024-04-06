#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-sqlforge:latest -f Dockerfile.agent .

echo 'Done...'
