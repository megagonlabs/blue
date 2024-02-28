#/bin/bash
echo 'Publishing User Agent...'

# tag and publish
docker tag blue-agent-user:latest megagonlabs/blue-agent-user:latest
docker push megagonlabs/blue-agent-user:latest

echo 'Done...'
