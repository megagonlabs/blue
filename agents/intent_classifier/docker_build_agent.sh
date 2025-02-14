#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-intent_classifier:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-intent_classifier:latest blue-agent-intent_classifier:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
