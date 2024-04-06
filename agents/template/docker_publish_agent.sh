#/bin/bash
echo 'Publishing Template Agent...'

# tag and publish
docker tag blue-agent-template:latest megagonlabs/blue-agent-template:latest
docker push megagonlabs/blue-agent-template:latest

echo 'Done...'
