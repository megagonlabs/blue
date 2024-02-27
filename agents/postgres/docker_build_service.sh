#/bin/bash
echo 'Building Postgres Service...'

# build docker
docker build -t blue-service-postgres:latest -f Dockerfile.service .
echo 'Done...'
