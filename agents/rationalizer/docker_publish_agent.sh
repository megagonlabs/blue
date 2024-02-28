#/bin/bash
echo 'Publishing Rationalizer Agent...'

# tag and publish
docker tag blue-agent-rationalizer:latest megagonlabs/blue-agent-rationalizer:latest
docker push megagonlabs/blue-agent-rationalizer:latest

echo 'Done...'
