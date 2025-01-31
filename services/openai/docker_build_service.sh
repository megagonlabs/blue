#/bin/bash
echo 'Building OpenAI Service...'

# build docker
docker build --no-cache -t blue-service-openai:latest -f Dockerfile.service .

# tag image
docker tag blue-service-openai:latest blue-service-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
