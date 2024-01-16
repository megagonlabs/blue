docker rm blue_agent_openai_gptplanner
# OpenAI websocket backend
docker compose -f $BLUE_INSTALL_DIR/agents/openai/docker-compose.yaml -p blue_service_openai up -d
# GPT Planer Agent
export GPT_PLANNER_PROPERTIES='{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"],"excludes":[]},"tags": ["PLAN"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:\n{input}",  "openai.temperature":0,"openai.max_tokens":512,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
echo "Bring up GPT PLANNER OPENAI agent using the following properties: $GPT_PLANNER_PROPERTIES"
docker run -e session=$1 -e properties="$GPT_PLANNER_PROPERTIES" -d --network="host" --name blue_agent_openai_gptplanner blue-agent-openai:latest