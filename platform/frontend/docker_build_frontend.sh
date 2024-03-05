#/bin/bash
echo 'Building Platform Frontend...'
echo 'Make sure to store fa.token in $BLUE_INSTALL_DIR/secrets/fa.token'
fa_token=$(cat $BLUE_INSTALL_DIR/secrets/fa.token)
# if no argument supplied
if [ -z "$fa_token" ]
    then
        read -p "Font Awesome Pro Package Token: " fa_token
fi

# build docker
docker build -t blue-platform-frontend:latest -f Dockerfile.frontend --build-arg fa_token=$fa_token .

echo 'Done...'
