#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-agent-nl2sql-e2e-fs:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-nl2sql-e2e-fs:latest blue-agent-nl2sql-e2e-fs:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
