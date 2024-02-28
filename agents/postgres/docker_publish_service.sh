#/bin/bash
echo 'Publishing Postgres Service...'

# tag and publish
docker tag blue-service-postgres:latest megagonlabs/blue-service-postgres:latest
docker push megagonlabs/blue-service-postgres:latest

echo 'Done...'
