#/bin/bash
echo 'Building Requestor Service...'

# build docker
docker build --no-cache -t blue-service-requestor:latest -f Dockerfile.service .

# tag image
docker tag blue-service-requestor:latest blue-service-requestor:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
