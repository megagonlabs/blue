docker container stop $(docker ps | grep 'websocket-service' | awk '{ print $1 }' | tr '\n' ' ' )
