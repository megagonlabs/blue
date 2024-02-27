#/bin/bash
echo 'Building...'

# build docker
docker build -t blue-service-websocket_counter:latest -f Dockerfile.service .
echo 'Done...'
