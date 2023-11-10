docker run -e text="$1" --network="host" --name title_recommendation_user -d blue-agent-simple_user

SESSION_ID=""
while [ -z "$SESSION_ID" ]; do
  SESSION_ID=$(docker logs title_recommendation_user 2>&1 | grep "Started session SESSION" | awk -F' ' '{print $NF}' | awk -F':' '{print $NF}')
  sleep 1
done

echo "SESSION_ID:" $SESSION_ID
