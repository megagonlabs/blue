docker rm blue_agent_observer
# Observer Agent
echo "Bring up OBSERVER agent:"
docker run -e session=$1 --network="host" --name blue_agent_observer blue-agent-observer:latest
