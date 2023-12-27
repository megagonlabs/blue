#/bin/bash
echo 'Building...'

# copy from agent shared lib
mkdir -p lib/agent & cp -r ../../agents/lib/* lib/agent/

# copy from agent shared lib
mkdir -p lib/platform & cp -r ../lib/* lib/platform/

# build docker
docker build -t blue-agentregistry:latest -f Dockerfile.agentregistry .
echo 'Done...'
