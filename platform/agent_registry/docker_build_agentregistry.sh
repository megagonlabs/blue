#/bin/bash
source $(dirname $0)/build_agentregistry.sh

# build docker
docker build -t blue-agentregistry:latest -f Dockerfile.agentregistry .

echo 'Done...'
