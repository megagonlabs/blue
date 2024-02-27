#/bin/bash

# USAGE: join_swarm worker|manager
# worker|manager: worker or manager type

# Extract saved manager ip and token, based on node type
IP_ADDRESS=$(cat .manager.ip)
TOKEN=$(cat .$1.token)

echo "Joining swarm on $IP_ADDRESS as $1"
docker swarm join --token $TOKEN $IP_ADDRESS:2377
echo "Done.."
echo "Use list_swarm to list nodes in the swarm."
echo "Use label_swarm_node to label node."
echo "Use leave_swarm to leave."
