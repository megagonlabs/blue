docker container stop $(docker ps | grep 'websocket' | awk '{ print $1 }' | tr '\n' ' ' )
