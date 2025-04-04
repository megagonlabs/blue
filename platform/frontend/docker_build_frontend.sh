#/bin/bash
echo "Building docker image ..."
echo "${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# fa token
echo "Make sure to store fa.token in $BLUE_INSTALL_DIR/secrets/fa.token"
fa_token=$(cat $BLUE_INSTALL_DIR/secrets/fa.token)
# if no argument supplied
if [ -z "$fa_token" ]
    then
        read -p "Font Awesome Pro Package Token: " fa_token
fi

# build docker
docker buildx build  --platform ${BLUE_BUILD_PLATFORM} ${BLUE_BUILD_CACHE_ARG} --build-arg BLUE_BUILD_CACHE_ARG --build-arg BLUE_BUILD_LIB_ARG --push -t ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend${BLUE_BUILD_IMG_SUFFIX}:${BLUE_DEPLOY_VERSION} -f Dockerfile.frontend \
    --build-arg git_short=$(git rev-parse --short HEAD) \
    --build-arg git_long=$(git rev-parse HEAD) \
    --build-arg git_branch=$(git rev-parse --abbrev-ref HEAD) \
    --build-arg fa_token=$fa_token .

echo 'Done...'

