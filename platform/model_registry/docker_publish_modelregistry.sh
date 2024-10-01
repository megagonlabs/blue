#/bin/bash
echo 'Publishing ModelRegistry...'

# tag and publish
docker tag blue-modelregistry:latest megagonlabs/blue-modelregistry:latest
docker tag blue-modelregistry:latest megagonlabs/blue-modelregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-modelregistry:latest
docker push megagonlabs/blue-modelregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
