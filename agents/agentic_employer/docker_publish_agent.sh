#/bin/bash
echo 'Publishing Agentic Employer Agent...'

# tag and publish
docker tag blue-agent-agentic_employer:latest megagonlabs/blue-agent-agentic_employer:latest
docker tag blue-agent-agentic_employer:latest megagonlabs/blue-agent-agentic_employer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-agentic_employer:latest
docker push megagonlabs/blue-agent-agentic_employer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
