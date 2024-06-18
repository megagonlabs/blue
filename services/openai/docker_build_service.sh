#/bin/bash
echo 'Building OpenAI Service...'

source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-openai:latest -f Dockerfile.service .

# tag image
docker tag blue-service-openai:latest blue-service-openai:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
