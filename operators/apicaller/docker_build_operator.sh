#/bin/bash
source $(dirname $0)/build_operator.sh

echo 'Building docker image...'

# build docker
docker build -t blue-operator-apicaller:latest -f Dockerfile.operator .

# tag image
docker tag blue-operator-apicaller:latest blue-operator-apicaller:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
