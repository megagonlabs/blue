# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml up -d
# Knowledge Grounding Agent
echo "Bring up KNOWLEDGE GROUNDING OPENAI agent:"
docker run -e session=$1 -e NEO4J_USER=$NEO4J_USER -e NEO4J_PWD=$NEO4J_PWD --network="host" -d blue-agent-knowledge-grounding:latest
# Rationalizer Agent
echo "Bring up RATIONALIZER OPENAI agent:"
docker run -e session=$1 -d --network="host" blue-agent-rationalizer:latest
