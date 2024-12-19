#/bin/bash
echo 'Publishing DATAPLANNER Agent...'

# tag and publish
docker tag blue-agent-data_planner:latest megagonlabs/blue-agent-data_planner:latest
docker tag blue-agent-data_planner:latest megagonlabs/blue-agent-data_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-data_planner:latest
docker push megagonlabs/blue-agent-data_plannere:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
