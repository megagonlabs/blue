#/bin/bash
echo 'Publishing API Agent...'

# tag and publish
docker tag blue-agent-api:latest megagonlabs/blue-agent-api:latest
docker push megagonlabs/blue-agent-api:latest

echo 'Done...'
