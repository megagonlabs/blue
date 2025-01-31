#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-websocket_counter:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-websocket_counter:latest blue-agent-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
