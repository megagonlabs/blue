#/bin/bash
echo 'Publishing NL2SQL Operator...'

# tag and publish
docker tag blue-operator-nl2sql:latest megagonlabs/blue-operator-nl2sql:latest
docker tag blue-operator-nl2sql:latest megagonlabs/blue-operator-nl2sql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-operator-nl2sql:latest
docker push megagonlabs/blue-operator-nl2sql:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
