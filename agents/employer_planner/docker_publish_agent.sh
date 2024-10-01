#/bin/bash
echo 'Publishing Employer Planner Agent...'

# tag and publish
docker tag blue-agent-employer_planner:latest megagonlabs/blue-agent-employer_planner:latest
docker tag blue-agent-employer_planner:latest megagonlabs/blue-agent-employer_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-employer_planner:latest
docker push megagonlabs/blue-agent-employer_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
