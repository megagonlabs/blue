#/bin/bash
echo 'Building...'

# build docker
docker build -t blue-service-neo4j:latest -f Dockerfile.service .
echo 'Done...'
