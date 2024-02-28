#/bin/bash
echo 'Publishing Neo4J Service...'

# tag and publish
docker tag blue-service-neo4j:latest megagonlabs/blue-service-neo4j:latest
docker push megagonlabs/blue-service-neo4j:latest

echo 'Done...'
