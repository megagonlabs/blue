#/bin/bash
echo 'Building Platform Frontend...'

# build docker
docker build -t blue-platform-frontend:latest -f Dockerfile.frontend .

echo 'Done...'
