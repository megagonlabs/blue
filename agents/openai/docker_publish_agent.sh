#/bin/bash
echo 'Publishing OpenAI Agent...'

# tag and publish
docker tag blue-agent-openai:latest megagonlabs/blue-agent-openai:latest
docker tag blue-agent-openai:latest megagonlabs/blue-agent-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-openai:latest
docker push megagonlabs/blue-agent-openai:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
