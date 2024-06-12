#/bin/bash
echo 'Publishing Neo4J Service...'

# tag and publish
docker tag blue-service-neo4j:latest megagonlabs/blue-service-neo4j:latest
docker tag blue-service-neo4j:latest megagonlabs/blue-service-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-neo4j:latest
docker push megagonlabs/blue-service-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
