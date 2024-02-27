docker rm blue_agent_simple_graph
# Reommender Agent
echo "Bring up RECOMMENDER agent:"
docker run -d --network="host" --name blue_agent_simple_graph blue-agent-simple_graph:latest --session $1 
