#/bin/bash
echo 'Publishing Form Agent...'

# tag and publish
docker tag blue-agent-form:latest megagonlabs/blue-agent-form:latest
docker tag blue-agent-form:latest megagonlabs/blue-agent-form:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-form:latest
docker push megagonlabs/blue-agent-form:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
