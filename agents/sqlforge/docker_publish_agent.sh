#/bin/bash
echo 'Publishing SQLForge Agent...'

# tag and publish
docker tag blue-agent-sqlforge:latest megagonlabs/blue-agent-sqlforge:latest
docker tag blue-agent-sqlforge:latest megagonlabs/blue-agent-sqlforge:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-sqlforge:latest
docker push megagonlabs/blue-agent-sqlforge:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
