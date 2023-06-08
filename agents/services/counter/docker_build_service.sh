#/bin/bash
echo 'Building...'

# build docker
docker build -t blue-service-counter:latest .
echo 'Done...'
