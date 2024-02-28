#/bin/bash
echo 'Publishing Neo4J Agent...'

# tag and publish
docker tag blue-agent-neo4j:latest megagonlabs/blue-agent-neo4j:latest
docker push megagonlabs/blue-agent-neo4j:latest

echo 'Done...'
