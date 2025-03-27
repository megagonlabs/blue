#/bin/bash
echo 'Publishing Visualizer Agent...'

# tag and publish
docker tag blue-agent-visualizer:latest megagonlabs/blue-agent-visualizer:latest
docker tag blue-agent-visualizer:latest megagonlabs/blue-agent-visualizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-visualizer:latest
docker push megagonlabs/blue-agent-visualizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
