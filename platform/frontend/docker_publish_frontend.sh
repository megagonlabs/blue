#/bin/bash
echo 'Publishing Platform Frontend...'

# tag and publish
docker tag blue-platform-frontend:latest megagonlabs/blue-platform-frontend:latest
docker push megagonlabs/blue-platform-frontend:latest

echo 'Done...'
