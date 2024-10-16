#/bin/bash
echo 'Publishing SQL_EXEC Agent...'

# tag and publish
docker tag blue-agent-sql-exec:latest megagonlabs/blue-agent-sql-exec:latest
docker tag blue-agent-sql-exec:latest megagonlabs/blue-agent-sql-exec:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-sql-exec:latest
docker push megagonlabs/blue-agent-sql-exec:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
