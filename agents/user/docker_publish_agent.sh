#/bin/bash
echo 'Publishing User Agent...'

# tag and publish
docker tag blue-agent-user:latest megagonlabs/blue-agent-user:latest
docker tag blue-agent-user:latest megagonlabs/blue-agent-user:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-user:latest
docker push megagonlabs/blue-agent-user:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
