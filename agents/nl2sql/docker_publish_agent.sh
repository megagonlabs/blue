#/bin/bash
echo 'Publishing NL2SQL Agent...'

# tag and publish
docker tag blue-agent-nl2sql:latest megagonlabs/blue-agent-nl2sql:latest
docker push megagonlabs/blue-agent-nl2sql:latest

echo 'Done...'
