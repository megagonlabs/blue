#/bin/bash
echo 'Publishing AgentRegistry...'

# tag and publish
docker tag blue-agentregistry:latest megagonlabs/blue-agentregistry:latest
docker push megagonlabs/blue-agentregistry:latest

echo 'Done...'
