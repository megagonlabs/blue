#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-job_search_planner:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-job_search_planner:latest blue-agent-job_search_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
