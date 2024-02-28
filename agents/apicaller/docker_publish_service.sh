#/bin/bash
echo 'Building API Agent Service...'

# build docker
docker build -t blue-service-websocket_counter:latest -f Dockerfile.service .

# tag and publish
docker tag blue-service-websocket_counter:latest megagonlabs/blue-service-websocket_counter:latest
docker push megagonlabs/blue-service-websocket_counter:latest

echo 'Done...'
