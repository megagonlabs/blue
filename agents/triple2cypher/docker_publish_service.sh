#/bin/bash
echo 'Building OpenAI Service...'

# tag and publish
docker tag blue-service-openai:latest megagonlabs/blue-service-openai:latest
docker push megagonlabs/blue-service-openai:latest

echo 'Done...'
