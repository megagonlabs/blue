#/bin/bash
echo 'Publishing Recorder Agent...'

# tag and publish
docker tag blue-agent-recorder:latest megagonlabs/blue-agent-recorder:latest
docker tag blue-agent-recorder:latest megagonlabs/blue-agent-recorder:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-recorder:latest
docker push megagonlabs/blue-agent-recorder:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
