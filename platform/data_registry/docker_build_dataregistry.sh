#/bin/bash
echo 'Building DataRegistry...'

# cleanup libs
rm -r lib

# copy from agent shared lib
mkdir -p lib/agent; cp -r ../../agents/lib/* lib/agent/

# copy from platform shared lib
mkdir -p lib/platform; cp -r ../lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# build docker
docker build -t blue-dataregistry:latest -f Dockerfile.dataregistry .
echo 'Done...'
