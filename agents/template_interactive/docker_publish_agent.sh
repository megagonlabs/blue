#/bin/bash
echo 'Publishing Template Interactive Agent...'

# tag and publish
docker tag blue-agent-template-interactive:latest megagonlabs/blue-agent-template-interactive:latest
docker tag blue-agent-template-interactive:latest megagonlabs/blue-agent-template-interactive:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-template-interactive:latest
docker push megagonlabs/blue-agent-template-interactive:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
