#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-platform-api:latest -f Dockerfile.api .

# tag image
docker tag blue-platform-api:latest blue-platform-api:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
