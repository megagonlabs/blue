#/bin/bash
echo 'Publishing DataRegistry...'

# tag and publish
docker tag blue-dataregistry:latest megagonlabs/blue-dataregistry:latest
docker tag blue-dataregistry:latest megagonlabs/blue-dataregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-dataregistry:latest
docker push megagonlabs/blue-dataregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
