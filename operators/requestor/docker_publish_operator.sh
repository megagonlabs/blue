#/bin/bash
echo 'Publishing API Operator...'

# tag and publish
docker tag blue-operator-api:latest megagonlabs/blue-operator-api:latest
docker tag blue-operator-api:latest megagonlabs/blue-operator-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-operator-api:latest
docker push megagonlabs/blue-operator-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
