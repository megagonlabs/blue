#/bin/bash
echo 'Publishing API Agent...'

# tag and publish
docker tag blue-agent-api:latest megagonlabs/blue-agent-api:latest
docker tag blue-agent-api:latest megagonlabs/blue-agent-api:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-api:latest
docker push megagonlabs/blue-agent-api:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
