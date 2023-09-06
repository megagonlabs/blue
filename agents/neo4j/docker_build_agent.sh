#/bin/bash
echo 'Building...'

# copy from shared lib
mkdir -p lib/shared & cp -r ../shared_lib/* lib/shared/

# build docker
docker build -t blue-agent-neo4j:latest -f Dockerfile.agent .
echo 'Done...'
