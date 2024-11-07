#/bin/bash
echo 'Publishing Clusterer Agent...'

# tag and publish
docker tag blue-agent-clusterer:latest megagonlabs/blue-agent-clusterer:latest
docker tag blue-agent-clusterer:latest megagonlabs/blue-agent-clusterer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-clusterer:latest
docker push megagonlabs/blue-agent-clusterer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
