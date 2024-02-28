#/bin/bash
echo 'Publishing Platform API...'

# tag and publish
docker tag blue-platform-api:latest megagonlabs/blue-platform-api:latest
docker push megagonlabs/blue-platform-api:latest

echo 'Done...'
