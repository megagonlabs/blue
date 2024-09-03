#/bin/bash
source $(dirname $0)/build_operator.sh

echo 'Building docker image...'

# build docker
docker build -t blue-operator-openai:latest -f Dockerfile.operator .

# tag image
docker tag blue-operator-openai:latest blue-operator-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
