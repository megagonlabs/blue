#/bin/bash
echo 'Publishing Platform API...'

# tag and publish
docker tag blue-platform-api:latest megagonlabs/blue-platform-api:latest
docker tag blue-platform-api:latest megagonlabs/blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-platform-api:latest
docker push megagonlabs/blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
