#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-apicaller:latest -f Dockerfile.agent .

echo 'Done...'
