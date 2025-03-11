#/bin/sh
export SECURE=${BLUE_DEPLOY_SECURE}
if [ -z ${SECURE} ]; then export SECURE=True; fi
export SECURE_LOWERCASE=$(echo ${SECURE}| tr '[:upper:]' '[:lower:]')
export PROTOCOL_SUFFIX="s"
if [[ "$SECURE_LOWERCASE" == "false" ]]; then
   export PROTOCOL_SUFFIX=""
fi
echo "NEXT_PUBLIC_REST_API_SERVER=http${PROTOCOL_SUFFIX}://${BLUE_PUBLIC_API_SERVER}:${BLUE_PUBLIC_API_SERVER_PORT}" >> .env.production
echo "NEXT_PUBLIC_WS_API_SERVER=ws${PROTOCOL_SUFFIX}://${BLUE_PUBLIC_API_SERVER}:${BLUE_PUBLIC_API_SERVER_PORT}" >> .env.production
echo "NEXT_PUBLIC_AGENT_REGISTRY_NAME=${BLUE_AGENT_REGISTRY}" >> .env.production
echo "NEXT_PUBLIC_DATA_REGISTRY_NAME=${BLUE_DATA_REGISTRY}" >> .env.production
echo "NEXT_PUBLIC_OPERATOR_REGISTRY_NAME=${BLUE_OPERATOR_REGISTRY}" >> .env.production
echo "NEXT_PUBLIC_MODEL_REGISTRY_NAME=${BLUE_MODEL_REGISTRY}" >> .env.production
echo "NEXT_PUBLIC_PLATFORM_NAME=${BLUE_DEPLOY_PLATFORM}" >> .env.production
npm run start
