#/bin/bash
echo 'Publishing JobSearch Agent...'

# tag and publish
docker tag blue-agent-job_search:latest megagonlabs/blue-agent-job_search:latest
docker push megagonlabs/blue-agent-job_search:latest

echo 'Done...'
