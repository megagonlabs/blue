#/bin/bash
echo 'Publishing Postgres Service...'

# tag and publish
docker tag blue-service-postgres:latest megagonlabs/blue-service-postgres:latest
docker tag blue-service-postgres:latest megagonlabs/blue-service-postgres:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-postgres:latest
docker push megagonlabs/blue-service-postgres:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
