#/bin/bash
echo 'Publishing Summarizer Agent...'

# tag and publish
docker tag blue-agent-summarizer:latest megagonlabs/blue-agent-summarizer:latest
docker tag blue-agent-summarizer:latest megagonlabs/blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-summarizer:latest
docker push megagonlabs/blue-agent-summarizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
