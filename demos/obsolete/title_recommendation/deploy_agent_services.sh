#/bin/bash
# neo4j
${BLUE_INSTALL_DIR}/platform/scripts/deploy_service.sh --port_mapping 8001:8001  --name neo4j --image blue-service-neo4j:latest
# openai
${BLUE_INSTALL_DIR}/platform/scripts/deploy_service.sh --port_mapping 8002:8001  --name openai --image blue-service-openai:latest --env-file ${BLUE_INSTALL_DIR}/agents/openai/openai.env
