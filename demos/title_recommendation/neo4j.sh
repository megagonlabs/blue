docker rm blue_agent_neo4j
docker compose -f $BLUE_INSTALL_DIR/agents/neo4j/docker-compose.yaml -p blue_service_neo4j up -d
export PROPERTIES='{"neo4j.user":"'"$NEO4J_USER"'","neo4j.password":"'"$NEO4J_PWD"'","neo4j.host":"'"$NEO4J_HOST"'"}'
docker run -e session=$1 -e properties="$PROPERTIES" -d --network="host" --name blue_agent_neo4j blue-agent-neo4j:latest 
