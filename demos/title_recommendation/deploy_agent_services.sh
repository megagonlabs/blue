#/bin/bash
# neo4j
${BLUE_INSTALL_DIR}/platform/scripts/deploy_service --port_mapping 8001:8001  --name blue_service_neo4j --image blue_service_neo4j:latest
# openai
${BLUE_INSTALL_DIR}/platform/scripts/deploy_service --port_mapping 8002:8001  --name blue_service_openai --image blue_service_openai:latest