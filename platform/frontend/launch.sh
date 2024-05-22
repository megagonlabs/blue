#/bin/sh
echo "NEXT_PUBLIC_REST_API_SERVER=https://${BLUE_PUBLIC_API_SERVER}" > .env.production
echo "NEXT_PUBLIC_WS_API_SERVER=wss://${BLUE_PUBLIC_API_SERVER}" >> .env.production
echo "NEXT_PUBLIC_AGENT_REGISTRY_NAME=${BLUE_AGENT_REGISTRY}" >> .env.production
echo "NEXT_PUBLIC_DATA_REGISTRY_NAME=${BLUE_DATA_REGISTRY}" >> .env.production
npm run build
npm run start
