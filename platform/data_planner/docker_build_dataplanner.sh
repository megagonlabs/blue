#/bin/bash
source $(dirname $0)/build_dataplanner.sh

# build docker
docker build -t blue-dataplanner:latest -f Dockerfile.dataplanner .

# tag image
docker tag blue-dataplanner:latest blue-dataplanner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'

