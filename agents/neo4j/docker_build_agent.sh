#/bin/bash
echo 'Building Neo4J Agent...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# build docker
docker build -t blue-agent-neo4j:latest -f Dockerfile.agent .
echo 'Done...'
