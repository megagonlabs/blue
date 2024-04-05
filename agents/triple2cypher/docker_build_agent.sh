#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-triple2cypher:latest -f Dockerfile.agent .

echo 'Done...'
