#/bin/bash
echo 'Publishing Counter Agent...'

# tag and publish
docker tag blue-agent-counter:latest megagonlabs/blue-agent-counter:latest
docker push megagonlabs/blue-agent-counter:latest
echo 'Done...'
