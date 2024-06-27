#/bin/bash
echo 'Publishing Planner Agent...'

# tag and publish
docker tag blue-agent-planner:latest megagonlabs/blue-agent-planner:latest
docker tag blue-agent-planner:latest megagonlabs/blue-agent-planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-planner:latest
docker push megagonlabs/blue-agent-planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
