#/bin/bash
source $(dirname $0)/build_agentregistry.sh

# build docker
docker build -t blue-agentregistry:latest -f Dockerfile.agentregistry .

# tag image
docker tag blue-agentregistry:latest blue-agentregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
