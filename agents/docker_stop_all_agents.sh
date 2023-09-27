docker container stop $(docker ps | grep 'blue-agent' | awk '{ print $1 }' | tr '\n' ' ' )
