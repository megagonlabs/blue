#/bin/bash
echo 'Building DSPy Service...'

source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-dspy:latest -f Dockerfile.service .

# tag image
docker tag blue-service-dspy:latest blue-service-dspy:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
