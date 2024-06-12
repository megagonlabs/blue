#/bin/bash
echo 'Publishing AgentRegistry...'

# tag and publish
docker tag blue-agentregistry:latest megagonlabs/blue-agentregistry:latest
docker tag blue-agentregistry:latest megagonlabs/blue-agentregistry:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agentregistry:latest
docker push megagonlabs/blue-agentregistry:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
