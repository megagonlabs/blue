#/bin/bash
echo 'Building Platform API...'

# cleanup libs
rm -r lib

# copy from platform shared lib
mkdir -p lib/platform; cp -r ../lib/* lib/platform/

# copy from agent shared lib
mkdir -p lib/agents; cp -r ../../agents/lib/* lib/agents/
mkdir -p lib/agents; cp -r ../../agents/observer/src/* lib/agents/

# copy from agent_registry shared lib
mkdir -p lib/agent_registry; cp -r ../agent_registry/src/* lib/agent_registry/

# copy from data_registry shared lib
mkdir -p lib/data_registry; cp -r ../data_registry/src/* lib/data_registry/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
