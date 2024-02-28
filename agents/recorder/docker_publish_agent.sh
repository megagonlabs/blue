#/bin/bash
echo 'Publishing Recorder Agent...'

# tag and publish
docker tag blue-agent-recorder:latest megagonlabs/blue-agent-recorder:latest
docker push megagonlabs/blue-agent-recorder:latest

echo 'Done...'
