docker rm blue_agent_user
docker run -d --network="host" --name blue_agent_user blue-agent-user --text "$1"

SESSION_ID=""
while [ -z "$SESSION_ID" ]; do
  SESSION_ID=$(docker logs blue_agent_user 2>&1 | grep "Started session SESSION" | awk -F' ' '{print $NF}' | awk -F':' '{print $NF}')
  sleep 1
done

echo "SESSION_ID:" SESSION:$SESSION_ID
