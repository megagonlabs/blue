#/bin/bash
echo 'Building...'

# copy from shared lib
mkdir -p lib/agent & cp -r ../lib/* lib/agent/

# build docker
docker build -t blue-agent-simple_user:latest -f Dockerfile.agent .
echo 'Done...'
