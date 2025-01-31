#/bin/bash
echo 'Publishing Presenter Agent...'

# tag and publish
docker tag blue-agent-presenter:latest megagonlabs/blue-agent-presenter:latest
docker tag blue-agent-presenter:latest megagonlabs/blue-agent-presenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-presenter:latest
docker push megagonlabs/blue-agent-presenter:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
