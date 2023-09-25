# Observer Agent
echo "Bring up OBSERVER agent:"
docker run -e session=$1 --network="host" blue-agent-observer:latest