#/bin/bash
echo 'Building WebSocketCounter Service...'

# build docker
docker build --no-cache -t blue-service-websocket_counter:latest -f Dockerfile.service .

# tag image
docker tag blue-service-websocket_counter:latest blue-service-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
