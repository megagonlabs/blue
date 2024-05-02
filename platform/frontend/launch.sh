#/bin/sh
echo "NEXT_PUBLIC_REST_API_SERVER=https://${BLUE_PUBLIC_API_SERVER}" > .env.production
echo "NEXT_PUBLIC_WS_API_SERVER=wss://${BLUE_PUBLIC_API_SERVER}" >> .env.production
npm run build
npm run start
