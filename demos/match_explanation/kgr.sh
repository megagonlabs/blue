docker rm blue_agent_knowledge_grounding
docker rm blue_agent_rationalizer
# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml -p blue_service_openai up -d
# Knowledge Grounding Agent
echo "Bring up KNOWLEDGE GROUNDING OPENAI agent:"
echo $1
echo $2
echo $3
echo $4
docker run -e profile="$1" -e title="$2" -e next_title="$3" -e session=$4 -e NEO4J_USER=$NEO4J_USER -e NEO4J_PWD=$NEO4J_PWD --network="host" --name blue_agent_knowledge_grounding -d blue-agent-knowledge_grounding:latest
# Rationalizer Agent
echo "Bring up RATIONALIZER OPENAI agent:"
docker run -e session=$1 -d --network="host" --name blue_agent_rationalizer blue-agent-rationalizer:latest
