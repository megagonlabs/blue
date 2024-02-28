#/bin/bash
echo 'Publishing DataRegistry...'

# tag and publish
docker tag blue-dataregistry:latest megagonlabs/blue-dataregistry:latest
docker push megagonlabs/blue-dataregistry:latest

echo 'Done...'
