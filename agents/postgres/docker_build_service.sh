#/bin/bash
echo 'Building...'

# build docker
docker build -t blue-service-postgres:latest -f Dockerfile.service .
echo 'Done...'
