export SESSION_ID=$(cat .sid)
export NEO4J_AGENT_PROPERTIES='{"neo4j.service":"ws://blue_service_neo4j:8001","neo4j.user":"'"${NEO4J_USER}"'","neo4j.password":"'"${NEO4J_PWD}"'","neo4j.host":"'"${NEO4J_HOST}"'"}'
blue session --session-id ${SESSION_ID} join --REGISTRY default --AGENT NEO4J --AGENT_PROPERTIES "${NEO4J_AGENT_PROPERTIES}" 
