#/bin/bash
echo 'Building OpenAI Service...'

# build docker
docker build -t blue-service-openai:latest -f Dockerfile.service .

echo 'Done...'
