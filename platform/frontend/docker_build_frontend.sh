#/bin/bash
echo 'Building Platform Frontend...'

fa_token=$1
# if no argument supplied
if [ -z "$fa_token" ]
    then
        read -p "Font Awesome Pro Package Token: " fa_token
fi

# build docker
docker build . --t blue-platform-frontend:latest -f Dockerfile.frontend --build-arg fa_token=$fa_token

echo 'Done...'