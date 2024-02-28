#/bin/bash
echo 'Publishing OpenAI Agent...'

# tag and publish
docker tag blue-agent-openai:latest megagonlabs/blue-agent-openai:latest
docker push megagonlabs/blue-agent-openai:latest

echo 'Done...'
