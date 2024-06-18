#/bin/bash
echo 'Publishing Platform Frontend...'

# tag and publish
docker tag blue-platform-frontend:latest megagonlabs/blue-platform-frontend:latest
docker tag blue-platform-frontend:latest megagonlabs/blue-platform-frontend:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-platform-frontend:latest
docker push megagonlabs/blue-platform-frontend:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
