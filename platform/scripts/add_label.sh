#/bin/bash

# USAGE: add_label label node
echo "Adding label $1 to node"
docker node update --label-add target=$1 $2
echo "Done.."
