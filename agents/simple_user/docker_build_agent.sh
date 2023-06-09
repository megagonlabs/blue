#/bin/bash
echo 'Building...'

# copy from shared lib
cp -r ../shared_lib/* lib/shared/

# build docker
docker build -t blue-agent-simple_user:latest -f Dockerfile.agent .
echo 'Done...'
