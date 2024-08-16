#/bin/bash
echo 'Publishing Intearactive Planner Agent...'

# tag and publish
docker tag blue-agent-interactive_planner:latest megagonlabs/blue-agent-interactive_planner:latest
docker tag blue-agent-interactive_planner:latest megagonlabs/blue-agent-interactive_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-interactive_planner:latest
docker push megagonlabs/blue-agent-interactive_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
