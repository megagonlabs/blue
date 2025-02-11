#/bin/bash
echo 'Building blue lib...'

# build 
python setup.py build
# dist
python setup.py sdist

