#/bin/bash
echo 'Building...'

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

mkdir -p lib/data_registry; cp -r ../../platform/data_registry/src/* lib/data_registry

cp -r ../../platform/lib/* lib/data_registry

# build docker
docker build -t blue-agent-knowledge_grounding:latest -f Dockerfile.agent .
echo 'Done...'
