#/bin/bash
echo 'Publishing Template Interactive Agent...'

# tag and publish
docker tag blue-agent-template-interactive:latest megagonlabs/blue-agent-template-interactive:latest
docker push megagonlabs/blue-agent-template-interactive:latest

echo 'Done...'
