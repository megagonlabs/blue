#/bin/bash
echo 'Reinstalling blue cli lib...'

# build 
./build.sh
./publish.sh
./uninstall.sh
./install.sh
