docker rm blue_agent_knowledge_grounding
docker rm blue_agent_rationalizer
# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml -p blue_service_openai up -d
# Knowledge Grounding Agent
echo "Bring up KNOWLEDGE GROUNDING OPENAI agent:"
docker run -d -e NEO4J_USER=$NEO4J_USER -e NEO4J_PWD=$NEO4J_PWD --network="host" --name blue_agent_knowledge_grounding blue-agent-knowledge_grounding:latest --session $1 
# Rationalizer Agent
echo "Bring up RATIONALIZER OPENAI agent:"
docker run -d --network="host" --name blue_agent_rationalizer blue-agent-rationalizer:latest --session $1 
