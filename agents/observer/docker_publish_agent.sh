#/bin/bash
echo 'Publishing Observer Agent...'

# tag and publish
docker tag blue-agent-observer:latest megagonlabs/blue-agent-observer:latest
docker tag blue-agent-observer:latest megagonlabs/blue-agent-observer:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-observer:latest
docker push megagonlabs/blue-agent-observer:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
