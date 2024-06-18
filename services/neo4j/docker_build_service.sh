#/bin/bash
echo 'Building Neo4J Service...'

source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-neo4j:latest -f Dockerfile.service .

# tag image
docker tag blue-service-neo4j:latest blue-service-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
