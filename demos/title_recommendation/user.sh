docker run -e text="$1" --network="host" --name blue_agent_simple_user -d blue-agent-simple_user

SESSION_ID=""
while [ -z "$SESSION_ID" ]; do
  SESSION_ID=$(docker logs blue_agent_simple_user 2>&1 | grep "Started session SESSION" | awk -F' ' '{print $NF}' | awk -F':' '{print $NF}')
  sleep 1
done

echo "SESSION_ID:" SESSION:$SESSION_ID
