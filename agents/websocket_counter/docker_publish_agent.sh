#/bin/bash
echo 'Publishing WebSocketCounter Agent...'

# tag and publish
docker tag blue-agent-websocket_counter:latest megagonlabs/blue-agent-websocket_counter:latest
docker push megagonlabs/blue-agent-websocket_counter:latest

echo 'Done...'
