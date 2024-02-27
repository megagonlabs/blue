docker rm blue_agent_observer
# Observer Agent
echo "Bring up OBSERVER agent:"
docker run --network="host" --name blue_agent_observer blue-agent-observer:latest --session $1 
