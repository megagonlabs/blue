#/bin/bash
echo 'Building APICaller Service...'

# build docker
docker build -t blue-service-apicaller:latest -f Dockerfile.service .

# tag and publish
docker tag blue-service-apicaller:latest megagonlabs/blue-service-apicaller:latest
docker tag blue-service-apicaller:latest megagonlabs/blue-service-apicaller:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-apicaller:latest
docker push megagonlabs/blue-service-apicaller:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
