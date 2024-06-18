#/bin/bash

# USAGE: init_swarm <SWARM_DIRECTORY>
# SWARM_DIRECTORY: directory to save/retrieve tokens 

IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "Initializing swarm with manager: $IP_ADDRESS"
echo $IP_ADDRESS > $1/.manager.ip
docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
docker swarm join-token manager -q > $1/.manager.token
docker swarm join-token worker -q > $1/.worker.token
echo "Done.."
echo "Use join_swarm.sh to add nodes to the swarm."
