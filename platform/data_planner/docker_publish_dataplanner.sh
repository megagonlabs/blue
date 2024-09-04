#/bin/bash
echo 'Publishing DataPlanner...'

# tag and publish
docker tag blue-dataplanner:latest megagonlabs/blue-dataplanner:latest
docker tag blue-dataplanner:latest megagonlabs/blue-dataplanner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-dataplanner:latest
docker push megagonlabs/blue-dataplanner:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
