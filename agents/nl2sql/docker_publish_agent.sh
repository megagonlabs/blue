#/bin/bash
echo 'Publishing NL2SQL Agent...'

# tag and publish
docker tag blue-agent-nl2sql:latest megagonlabs/blue-agent-nl2sql:latest
docker tag blue-agent-nl2sql:latest megagonlabs/blue-agent-nl2sql:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-nl2sql:latest
docker push megagonlabs/blue-agent-nl2sql:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
