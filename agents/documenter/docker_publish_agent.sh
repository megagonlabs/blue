#/bin/bash
echo 'Publishing Documenter Agent...'

# tag and publish
docker tag blue-agent-documenter:latest megagonlabs/blue-agent-documenter:latest
docker tag blue-agent-documenter:latest megagonlabs/blue-agent-documenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-documenter:latest
docker push megagonlabs/blue-agent-documenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
