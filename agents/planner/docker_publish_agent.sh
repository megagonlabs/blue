#/bin/bash
echo 'Publishing Planner Agent...'

# tag and publish
docker tag blue-agent-planner:latest megagonlabs/blue-agent-planner:latest
docker push megagonlabs/blue-agent-planner:latest

echo 'Done...'
