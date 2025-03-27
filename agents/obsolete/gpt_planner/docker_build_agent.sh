#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-gpt_planner:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-gpt_planner:latest blue-agent-gpt_planner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
