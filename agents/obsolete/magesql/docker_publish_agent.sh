#/bin/bash
echo 'Publishing MAGESQL Agent...'

# tag and publish
docker tag blue-agent-magesql:latest megagonlabs/blue-agent-magesql:latest
docker tag blue-agent-magesql:latest megagonlabs/blue-agent-magesql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-magesql:latest
docker push megagonlabs/blue-agent-magesql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
