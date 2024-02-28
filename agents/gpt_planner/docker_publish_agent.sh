#/bin/bash
echo 'Publishing GPT Planner Agent...'

# tag and publish
docker tag blue-agent-gpt_planner:latest megagonlabs/blue-agent-gpt_planner:latest
docker push megagonlabs/blue-agent-gpt_planner:latest

echo 'Done...'
