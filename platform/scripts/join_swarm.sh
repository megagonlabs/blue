#/bin/bash

# USAGE: join_swarm worker|manager <SWARM_DIRECTORY>
# worker|manager: worker or manager type
# SWARM_DIRECTORY: directory to save/retrieve tokens

# Extract saved manager ip and token, based on node type
IP_ADDRESS=$(cat $2/.manager.ip)
TOKEN=$(cat $2/.$1.token)

echo "Joining swarm on $IP_ADDRESS as $1"
docker swarm join --token $TOKEN $IP_ADDRESS:2377
echo "Done.."
echo "Use list_swarm to list nodes in the swarm."
echo "Use label_swarm_node to label node."
echo "Use leave_swarm to leave."
