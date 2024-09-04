#/bin/bash
echo 'Building DataPlanner...'

# cleanup libs
rm -r lib

# copy from operator shared lib
mkdir -p lib/operator; cp -r ../../operators/lib/* lib/operator/

# copy from platform shared lib
mkdir -p lib/platform; cp -r ../lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
