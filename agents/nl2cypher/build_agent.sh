#/bin/bash
echo 'Building Nl2Cypher Agent...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from api agent lib
mkdir -p lib/apicaller; cp -r ../apicaller/src/* lib/apicaller/

# copy from openai agent lib
mkdir -p lib/openai; cp -r ../openai/src/* lib/openai/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# copy from data_registry lib
mkdir -p lib/data_registry; cp -r ../../platform/data_registry/src/* lib/data_registry

# copy common requirements
cp ../requirements.common.txt src/

cp lib/data_registry/requirements.txt src/requirements.data_registry.txt

echo 'Done...'
