#/bin/bash
source $(dirname $0)/build_agent.sh

echo 'Building docker image...'

# build docker
docker build -t blue-platform-api:latest -f Dockerfile.api .

# tag image
docker tag blue-platform-api:latest blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

# tag image
docker tag blue-platform-api:latest blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
