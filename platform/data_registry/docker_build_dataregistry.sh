#/bin/bash
source $(dirname $0)/build_dataregistry.sh

# build docker
docker build -t blue-dataregistry:latest -f Dockerfile.dataregistry .

# tag image
docker tag blue-dataregistry:latest blue-dataregistry:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'

