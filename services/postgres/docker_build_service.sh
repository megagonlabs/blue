#/bin/bash
echo 'Building Postgres Service...'

source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-postgres:latest -f Dockerfile.service .

# tag image
docker tag blue-service-postgres:latest blue-service-postgres:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
