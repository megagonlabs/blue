docker rm blue_agent_openai_gptplanner
# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml -p blue_service_openai up -d
# GPT Planer Agent
export GPT_PLANNER_PROPERTIES='{}'
echo "Bring up GPT PLANNER OPENAI agent using the following properties: $GPT_PLANNER_PROPERTIES"
docker run -d --network="host" --name blue_agent_gpt_planner blue-agent-gpt_planner:latest --session $1 --properties "$GPT_PLANNER_PROPERTIES"
