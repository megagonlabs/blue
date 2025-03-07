#/bin/bash
echo "Building docker image ..."
echo "${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:${BLUE_DEPLOY_VERSION}"

# fa token
echo "Make sure to store fa.token in $BLUE_INSTALL_DIR/secrets/fa.token"
fa_token=$(cat $BLUE_INSTALL_DIR/secrets/fa.token)
# if no argument supplied
if [ -z "$fa_token" ]
    then
        read -p "Font Awesome Pro Package Token: " fa_token
fi

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_CORE_DOCKER_ORG}/blue-platform-frontend:${BLUE_DEPLOY_VERSION} -f Dockerfile.frontend \
    --build-arg git_short=$(git rev-parse --short HEAD) \
    --build-arg git_long=$(git rev-parse HEAD) \
    --build-arg git_branch=$(git rev-parse --abbrev-ref HEAD) \
    --build-arg fa_token=$fa_token .

echo 'Done...'

