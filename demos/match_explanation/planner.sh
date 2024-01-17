docker rm blue_agent_openai_gptplanner
# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml -p blue_service_openai up -d
# GPT Planer Agent
export GPT_PLANNER_PROPERTIES='{}'
echo "Bring up GPT PLANNER OPENAI agent using the following properties: $GPT_PLANNER_PROPERTIES"
docker run -e session=$1 -e properties="$GPT_PLANNER_PROPERTIES" -d --network="host" --name blue_agent_gpt_planner blue-agent-gpt_planner:latest
