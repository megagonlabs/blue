#/bin/bash
echo 'Publishing OpenAI Operator...'

# tag and publish
docker tag blue-operator-openai:latest megagonlabs/blue-operator-openai:latest
docker tag blue-operator-openai:latest megagonlabs/blue-operator-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-operator-openai:latest
docker push megagonlabs/blue-operator-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
