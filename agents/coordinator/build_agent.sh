#/bin/bash
echo 'Building Coordinator Agent...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from data_planner lib
mkdir -p lib/data_planner; cp -r ../../platform/data_planner/src/* lib/data_planner/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
