#/bin/bash
echo 'Publishing NL2SQL_E2E_FS Agent...'

# tag and publish
docker tag blue-agent-nl2sql-e2e-fs:latest megagonlabs/blue-agent-nl2sql-e2e-fs:latest
docker tag blue-agent-nl2sql-e2e-fs:latest megagonlabs/blue-agent-nl2sql-e2e-fs:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-nl2sql-e2e-fs:latest
docker push megagonlabs/blue-agent-nl2sql-e2e-fs:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
