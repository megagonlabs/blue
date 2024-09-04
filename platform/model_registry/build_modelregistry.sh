#/bin/bash
echo 'Building ModelRegistry...'

# cleanup libs
rm -r lib

# copy from platform shared lib
mkdir -p lib/platform; cp -r ../lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
