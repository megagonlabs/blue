#/bin/bash
echo 'Publishing Nl2Cypher Agent...'

# tag and publish
docker tag blue-agent-nl2cypher:latest megagonlabs/blue-agent-nl2cypher:latest
docker tag blue-agent-nl2cypher:latest megagonlabs/blue-agent-nl2cypher:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-nl2cypher:latest
docker push megagonlabs/blue-agent-nl2cypher:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
