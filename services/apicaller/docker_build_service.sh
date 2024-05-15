#/bin/bash
source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-apicaller:latest -f Dockerfile.service .

echo 'Done...'
