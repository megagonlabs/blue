#/bin/bash
echo 'Building...'

# copy from shared lib
mkdir -p lib/agent & cp -r ../../agents/lib/* lib/agent/

# copy from platform shared lib
mkdir -p lib/platform & cp -r ../lib/* lib/platform/

# build docker
docker build -t blue-dataregistry:latest -f Dockerfile.dataregistry .
echo 'Done...'
