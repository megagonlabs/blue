#/bin/bash
echo 'Publishing Requestor Agent...'

# tag and publish
docker tag blue-agent-requestor:latest megagonlabs/blue-agent-requestor:latest
docker tag blue-agent-requestor:latest megagonlabs/blue-agent-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-requestor:latest
docker push megagonlabs/blue-agent-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
