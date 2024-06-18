#/bin/bash

# USAGE: remove_label label node
echo "Removing node label $1"
docker node update --label-rm target=$1 $2
echo "Done.."
