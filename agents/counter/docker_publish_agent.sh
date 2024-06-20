#/bin/bash
echo 'Publishing Counter Agent...'

# tag and publish
docker tag blue-agent-counter:latest megagonlabs/blue-agent-counter:latest
docker tag blue-agent-counter:latest megagonlabs/blue-agent-counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-counter:latest
docker push megagonlabs/blue-agent-counter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
