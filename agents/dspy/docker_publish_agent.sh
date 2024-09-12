#/bin/bash
echo 'Publishing DSPy Agent...'

# tag and publish
docker tag blue-agent-dspy:latest megagonlabs/blue-agent-dspy:latest
docker tag blue-agent-dspy:latest megagonlabs/blue-agent-dspy:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-dspy:latest
docker push megagonlabs/blue-agent-dspy:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
