#/bin/bash
echo 'Building...'

# copy from shared lib
mkdir -p lib/agent & cp -r ../../agents/lib/* lib/agent/

# build docker
docker build -t blue-agentregistry:latest -f Dockerfile.agentregistry .
echo 'Done...'
