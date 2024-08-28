#/bin/bash
echo 'Publishing OperatorRegistry...'

# tag and publish
docker tag blue-operatorregistry:latest megagonlabs/blue-operatorregistry:latest
docker tag blue-operatorregistry:latest megagonlabs/blue-operatorregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-operatorregistry:latest
docker push megagonlabs/blue-operatorregistry:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
