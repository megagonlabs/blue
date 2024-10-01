#/bin/bash
echo 'Publishing NL2SQL_E2E Agent...'

# tag and publish
docker tag blue-agent-nl2sql-e2e:latest megagonlabs/blue-agent-nl2sql-e2e:latest
docker tag blue-agent-nl2sql-e2e:latest megagonlabs/blue-agent-nl2sql-e2e:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-nl2sql-e2e:latest
docker push megagonlabs/blue-agent-nl2sql-e2e:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
