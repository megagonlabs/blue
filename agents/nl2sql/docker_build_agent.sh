#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-nl2sql:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-nl2sql:latest blue-agent-nl2sql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
