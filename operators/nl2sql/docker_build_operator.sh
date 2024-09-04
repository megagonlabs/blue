#/bin/bash
source $(dirname $0)/build_operator.sh

echo 'Building docker image...'

# build docker
docker build -t blue-operator-nl2sql:latest -f Dockerfile.operator .

# tag image
docker tag blue-operator-nl2sql:latest blue-operator-nl2sql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
