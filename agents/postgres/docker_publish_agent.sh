#/bin/bash
echo 'Publishing Postgres Agent...'

# tag and publish
docker tag blue-agent-postgres:latest megagonlabs/blue-agent-postgres:latest
docker tag blue-agent-postgres:latest megagonlabs/blue-agent-postgres:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-postgres:latest
docker push megagonlabs/blue-agent-postgres:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
