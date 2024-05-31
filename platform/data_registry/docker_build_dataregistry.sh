#/bin/bash
source $(dirname $0)/build_dataregistry.sh

# build docker
docker build -t blue-dataregistry:latest -f Dockerfile.dataregistry .

echo 'Done...'

