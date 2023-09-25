# Reommender Agent
echo "Bring up RECOMMENDER agent:"
docker run -e session=$1 -d --network="host" blue-agent-simple_graph:latest