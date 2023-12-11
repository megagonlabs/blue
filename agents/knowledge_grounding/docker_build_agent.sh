#/bin/bash
echo 'Building...'

# copy from agent lib
mkdir -p lib/agent & cp -r ../lib/* lib/agent/

# build docker
docker build -t blue-agent-knowledge_grounding:latest -f Dockerfile.agent .
echo 'Done...'
