docker compose -f $BLUE_INSTALL_DIR/agents/neo4j/docker-compose.yaml up -d
export PROPERTIES='{"neo4j.user":"'"$NEO4J_USER"'","neo4j.password":"'"$NEO4J_PWD"'","neo4j.host":"bolt://18.216.233.236/"}'
docker run -e session=$1 -e properties="$PROPERTIES" -d --network="host" blue-agent-neo4j:latest 
