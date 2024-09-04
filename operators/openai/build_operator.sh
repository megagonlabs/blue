#/bin/bash
echo 'Building OpenAI Operator...'

echo 'Copying libs...'

# cleanup libs
rm -r lib


# copy from operator lib
mkdir -p lib/operator; cp -r ../lib/* lib/operator/

# copy from api operator lib
mkdir -p lib/apicaller; cp -r ../apicaller/src/* lib/apicaller/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
