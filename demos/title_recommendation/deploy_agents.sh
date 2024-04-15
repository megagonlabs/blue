#/bin/bash

## deploy agents from default registry with default properties

# deplotdeploy user agentt
${BLUE_INSTALL_DIR}/platform/scripts/deploy_agent.sh --agent User --image blue-agent-user:latest
# deploy neo4j agent
${BLUE_INSTALL_DIR}/platform/scripts/deploy_agent.sh --agent NEO4J --image blue-agent-neo4j:latest
