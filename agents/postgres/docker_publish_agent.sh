#/bin/bash
echo 'Publishing Postgres Agent...'

# tag and publish
docker tag blue-agent-postgres:latest megagonlabs/blue-agent-postgres:latest
docker push megagonlabs/blue-agent-postgres:latest

echo 'Done...'
