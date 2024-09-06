#/bin/bash
echo 'Publishing Job Search Planner Agent...'

# tag and publish
docker tag blue-agent-job_search_planner:latest megagonlabs/blue-agent-job_search_planner:latest
docker tag blue-agent-job_search_planner:latest megagonlabs/blue-agent-job_search_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-job_search_planner:latest
docker push megagonlabs/blue-agent-job_search_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
