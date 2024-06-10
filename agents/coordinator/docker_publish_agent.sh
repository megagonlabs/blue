#/bin/bash
echo 'Publishing Coordinator Agent...'

# tag and publish
docker tag blue-agent-coordinator:latest megagonlabs/blue-agent-coordinator:latest
docker push megagonlabs/blue-agent-coordinator:latest

echo 'Done...'
