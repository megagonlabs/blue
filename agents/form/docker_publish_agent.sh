#/bin/bash
echo 'Publishing Form Agent...'

# tag and publish
docker tag blue-agent-form:latest megagonlabs/blue-agent-form:latest
docker push megagonlabs/blue-agent-form:latest

echo 'Done...'
