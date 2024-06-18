#/bin/bash
echo 'Publishing ChatGPT Agent...'

# tag and publish
docker tag blue-agent-chatgpt:latest megagonlabs/blue-agent-chatgpt:latest
docker tag blue-agent-chatgpt:latest megagonlabs/blue-agent-chatgpt:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-chatgpt:latest
docker push megagonlabs/blue-agent-chatgpt:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
