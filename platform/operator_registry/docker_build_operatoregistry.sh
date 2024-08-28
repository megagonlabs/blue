#/bin/bash
source $(dirname $0)/build_operatorregistry.sh

# build docker
docker build -t blue-operatorregistry:latest -f Dockerfile.operatorregistry .

# tag image
docker tag blue-operatorregistry:latest blue-operatorregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'