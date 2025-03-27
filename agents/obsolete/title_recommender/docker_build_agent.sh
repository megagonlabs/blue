#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-title_recommender:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-title_recommender:latest blue-agent-title_recommender:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
