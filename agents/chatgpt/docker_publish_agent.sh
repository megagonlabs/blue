#/bin/bash
echo 'Publishing ChatGPT Agent...'

# tag and publish
docker tag blue-agent-chatgpt:latest megagonlabs/blue-agent-chatgpt:latest
docker push megagonlabs/blue-agent-chatgpt:latest

echo 'Done...'
