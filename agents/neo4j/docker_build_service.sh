#/bin/bash
echo 'Building Neo4J Service...'

# build docker
docker build -t blue-service-neo4j:latest -f Dockerfile.service .
echo 'Done...'
