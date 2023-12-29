#/bin/bash
echo 'Building...'

# copy from agent shared lib
mkdir -p lib/agent; cp -r ../../agents/lib/* lib/agent/

# copy from platform shared lib
mkdir -p lib/platform; cp -r ../lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# build docker
docker build -t blue-agentregistry:latest -f Dockerfile.agentregistry .
echo 'Done...'
