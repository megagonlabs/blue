#/bin/bash
echo 'Publishing Knowledge Grounding Agent ...'

# tag and publish
docker tag blue-agent-knowledge_grounding:latest megagonlabs/blue-agent-knowledge_grounding:latest
docker tag blue-agent-knowledge_grounding:latest megagonlabs/blue-agent-knowledge_grounding:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-knowledge_grounding:latest
docker push megagonlabs/blue-agent-knowledge_grounding:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
