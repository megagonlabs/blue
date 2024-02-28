#/bin/bash
echo 'Publishing WebSocketCounter Service...'

# tag and publish
docker tag blue-service-websocket_counter:latest megagonlabs/blue-service-websocket_counter:latest
docker push megagonlabs/blue-service-websocket_counter:latest

echo 'Done...'
