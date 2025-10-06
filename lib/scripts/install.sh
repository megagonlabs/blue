#/bin/bash
echo 'Installing blue lib...'

# install
pip install ${BLUE_BUILD_CACHE_ARG} ${BLUE_BUILD_LIB_ARG} blue-platform==${BLUE_DEPLOY_VERSION}
