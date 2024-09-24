#/bin/bash
docker image ls | grep megagon | grep agent | grep latest | awk ' { print $1 }' | xargs -L 1 -I dimage /bin/bash -c 'docker image pull dimage:latest'
