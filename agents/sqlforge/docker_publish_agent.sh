#/bin/bash
echo 'Publishing SQLForge Agent...'

# tag and publish
docker tag blue-agent-sqlforge:latest megagonlabs/blue-agent-sqlforge:latest
docker push megagonlabs/blue-agent-sqlforge:latest

echo 'Done...'
