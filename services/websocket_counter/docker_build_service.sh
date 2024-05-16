#/bin/bash
echo 'Building WebSocketCounter Service...'

source $(dirname $0)/build_service.sh

echo 'Building docker image...'

# build docker
docker build -t blue-service-websocket_counter:latest -f Dockerfile.service .

echo 'Done...'
