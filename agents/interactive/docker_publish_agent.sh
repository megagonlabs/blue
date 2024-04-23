#/bin/bash
echo 'Publishing Interactive Agent...'

# tag and publish
docker tag blue-agent-interactive:latest megagonlabs/blue-agent-interactive:latest
docker push megagonlabs/blue-agent-interactive:latest

echo 'Done...'
