export SESSION_ID=$(cat .sid)
echo ${SESSION_ID}
export USER_AGENT_PROPERTIES='{"tags": ["USER"]}'
blue session --session-id ${SESSION_ID} join --REGISTRY default --AGENT User --AGENT_PROPERTIES "${USER_AGENT_PROPERTIES}" --AGENT_INPUT "$1" 
