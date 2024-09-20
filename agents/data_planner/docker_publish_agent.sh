#/bin/bash
echo 'Publishing DATA_PLANNER Agent...'

# tag and publish
docker tag blue-agent-data-planner:latest megagonlabs/blue-agent-data-planner:latest
docker tag blue-agent-data-planner:latest megagonlabs/blue-agent-data-planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-data-planner:latest
docker push megagonlabs/blue-agent-data-plannere:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
