#/bin/bash
echo 'Publishing JobSearch Agent...'

# tag and publish
docker tag blue-agent-job_search:latest megagonlabs/blue-agent-job_search:latest
docker tag blue-agent-job_search:latest megagonlabs/blue-agent-job_search:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-job_search:latest
docker push megagonlabs/blue-agent-job_search:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
