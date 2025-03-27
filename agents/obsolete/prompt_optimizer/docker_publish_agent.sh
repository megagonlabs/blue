#/bin/bash
echo 'Publishing Prompt Optimizer Agent...'

# tag and publish
docker tag blue-agent-prompt_optimizer:latest megagonlabs/blue-agent-prompt_optimizer:latest
docker tag blue-agent-prompt_optimizer:latest megagonlabs/blue-agent-prompt_optimizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-prompt_optimizer:latest
docker push megagonlabs/blue-agent-prompt_optimizer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
