#/bin/bash
source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-apicaller:latest -f Dockerfile.service .

# tag image
docker tag blue-service-apicaller:latest blue-service-apicaller:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
