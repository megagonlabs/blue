#/bin/bash
echo 'Publishing Observer Agent...'

# tag and publish
docker tag blue-agent-observer:latest megagonlabs/blue-agent-observer:latest
docker push megagonlabs/blue-agent-observer:latest

echo 'Done...'
