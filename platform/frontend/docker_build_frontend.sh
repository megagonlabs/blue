#/bin/bash
echo 'Building Platform Frontend...'
echo "Make sure to store fa.token in $BLUE_INSTALL_DIR/secrets/fa.token"
fa_token=$(cat $BLUE_INSTALL_DIR/secrets/fa.token)
# if no argument supplied
if [ -z "$fa_token" ]
    then
        read -p "Font Awesome Pro Package Token: " fa_token
fi

# build docker
docker build --no-cache -t blue-platform-frontend:latest -f Dockerfile.frontend \
    --build-arg git_short=$(git rev-parse --short HEAD) \
    --build-arg git_long=$(git rev-parse HEAD) \
    --build-arg git_branch=$(git rev-parse --abbrev-ref HEAD) \
    --build-arg fa_token=$fa_token .

# tag image
docker tag blue-platform-frontend:latest blue-platform-frontend:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
