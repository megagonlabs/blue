#/bin/bash
echo 'Building OpenAI Service...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from service lib
mkdir -p lib/service; cp -r ../lib/* lib/service/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
