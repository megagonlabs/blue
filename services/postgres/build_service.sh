#/bin/bash
echo 'Building Postgres Service...'

echo 'Copying libs...'

# cleanup libs
rm -r lib

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

echo 'Done...'
