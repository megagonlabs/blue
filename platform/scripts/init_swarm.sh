#/bin/bash

# USAGE: init_swarm

IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "Initializing swarm with manager: $IP_ADDRESS"
echo $IP_ADDRESS > .manager.ip
docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
docker swarm join-token manager -q > .manager.token
docker swarm join-token worker -q > .worker.token
echo "Done.."
echo "Use join_swarm.sh to add nodes to the swarm."
