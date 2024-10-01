#/bin/bash
source $(dirname $0)/build_modelregistry.sh

# build docker
docker build -t blue-modelregistry:latest -f Dockerfile.modelregistry .

# tag image
docker tag blue-modelregistry:latest blue-modelregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'