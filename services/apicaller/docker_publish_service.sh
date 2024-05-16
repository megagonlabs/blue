#/bin/bash
echo 'Building APICaller Service...'

# build docker
docker build -t blue-service-apicaller:latest -f Dockerfile.service .

# tag and publish
docker tag blue-service-apicaller:latest megagonlabs/blue-service-apicaller:latest
docker push megagonlabs/blue-service-apicaller:latest

echo 'Done...'
