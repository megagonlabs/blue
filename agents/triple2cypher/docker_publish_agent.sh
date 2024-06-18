#/bin/bash
echo 'Publishing Triple2Cypher Agent...'

# tag and publish
docker tag blue-agent-triple2cypher:latest megagonlabs/blue-agent-triple2cypher:latest
docker tag blue-agent-triple2cypher:latest megagonlabs/blue-agent-triple2cypher:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-triple2cypher:latest
docker push megagonlabs/blue-agent-triple2cypher:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
