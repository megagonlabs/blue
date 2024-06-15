#/bin/bash
echo 'Publishing Rationalizer Agent...'

# tag and publish
docker tag blue-agent-rationalizer:latest megagonlabs/blue-agent-rationalizer:latest
docker tag blue-agent-rationalizer:latest megagonlabs/blue-agent-rationalizer:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-rationalizer:latest
docker push megagonlabs/blue-agent-rationalizer:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
