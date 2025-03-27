#/bin/bash
echo 'Publishing API Agent...'

# tag and publish
docker tag blue-agent-apicaller:latest megagonlabs/blue-agent-apicaller:latest
docker tag blue-agent-apicaller:latest megagonlabs/blue-agent-apicaller:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-apicaller:latest
docker push megagonlabs/blue-agent-apicaller:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
