#/bin/bash
echo 'Building Knowledge Grounding Agent ...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# copy from data_registry lib
mkdir -p lib/data_registry; cp -r ../../platform/data_registry/src/* lib/data_registry

echo 'Done...'
