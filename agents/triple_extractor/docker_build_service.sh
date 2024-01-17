#/bin/bash
echo 'Building...'

# build docker
docker build -t blue-service-openai:latest -f Dockerfile.service .
echo 'Done...'
