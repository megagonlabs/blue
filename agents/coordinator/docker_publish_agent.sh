#/bin/bash
echo 'Publishing Coordinator Agent...'

# tag and publish
docker tag blue-agent-coordinator:latest megagonlabs/blue-agent-coordinator:latest
docker tag blue-agent-coordinator:latest megagonlabs/blue-agent-coordinator:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-coordinator:latest
docker push megagonlabs/blue-agent-coordinator:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
