#/bin/bash
echo 'Installing blue cli lib...'

# install
pip install ${BLUE_BUILD_CACHE_ARG} ${BLUE_BUILD_LIB_ARG} blue-cli==${BLUE_DEPLOY_VERSION}
