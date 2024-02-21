docker rm blue_agent_sqlforge
# SQLForge Agent
echo "Bring up SQFORGE agent:"
docker run -e session=$1 --network="host" --name blue_agent_sqlforge -d blue-agent-sqlforge:latest
