#/bin/bash
echo 'Building ChatGPT Agent...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from api agent lib
mkdir -p lib/apicaller; cp -r ../api/src/* lib/apicaller/

# copy from openai agent lib
mkdir -p lib/openai; cp -r ../openai/src/* lib/openai/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
