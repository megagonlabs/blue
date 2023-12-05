docker container stop $(docker ps | grep 'blue_agent' | awk '{ print $1 }' | tr '\n' ' ' )
