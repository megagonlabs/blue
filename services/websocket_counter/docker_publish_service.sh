#/bin/bash
echo 'Publishing WebSocketCounter Service...'

# tag and publish
docker tag blue-service-websocket_counter:latest megagonlabs/blue-service-websocket_counter:latest
docker tag blue-service-websocket_counter:latest megagonlabs/blue-service-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-websocket_counter:latest
docker push megagonlabs/blue-service-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
