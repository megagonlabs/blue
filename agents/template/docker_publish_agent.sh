#/bin/bash
echo 'Publishing Template Agent...'

# tag and publish
docker tag blue-agent-template:latest megagonlabs/blue-agent-template:latest
docker tag blue-agent-template:latest megagonlabs/blue-agent-template:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-template:latest
docker push megagonlabs/blue-agent-template:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
