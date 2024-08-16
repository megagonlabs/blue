#/bin/bash
echo 'Publishing WebSocketCounter Agent...'

# tag and publish
docker tag blue-agent-websocket_counter:latest megagonlabs/blue-agent-websocket_counter:latest
docker tag blue-agent-websocket_counter:latest megagonlabs/blue-agent-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-websocket_counter:latest
docker push megagonlabs/blue-agent-websocket_counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
