#/bin/bash
echo 'Publishing OpenAI Service...'

# tag and publish
docker tag blue-service-openai:latest megagonlabs/blue-service-openai:indeed
docker tag blue-service-openai:latest megagonlabs/blue-service-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-openai:indeed
docker push megagonlabs/blue-service-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
