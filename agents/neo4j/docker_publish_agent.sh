#/bin/bash
echo 'Publishing Neo4J Agent...'

# tag and publish
docker tag blue-agent-neo4j:latest megagonlabs/blue-agent-neo4j:latest
docker tag blue-agent-neo4j:latest megagonlabs/blue-agent-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-neo4j:latest
docker push megagonlabs/blue-agent-neo4j:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
