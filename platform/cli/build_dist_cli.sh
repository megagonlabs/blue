#/bin/bash
echo 'Building blue cli...'

# build 
python setup.py build
# dist
python setup.py sdist

