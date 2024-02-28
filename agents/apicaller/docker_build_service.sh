#/bin/bash
echo 'Building API Agent Service...'

# tag and publish
docker tag blue-service-apicaller:latest megagonlabs/blue-service-apicaller:latest
docker push megagonlabs/blue-service-apiicaller:latest

echo 'Done...'
