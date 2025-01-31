#/bin/bash
echo 'Building Requestor Service...'

# build docker
docker build --no-cache -t blue-service-requestor:latest -f Dockerfile.service .

# tag and publish
docker tag blue-service-requestor:latest megagonlabs/blue-service-requestor:latest
docker tag blue-service-requestor:latest megagonlabs/blue-service-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-requestor:latest
docker push megagonlabs/blue-service-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
