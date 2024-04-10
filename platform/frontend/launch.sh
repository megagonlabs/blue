#/bin/sh
echo "NEXT_PUBLIC_REST_API_SERVER=http://${BLUE_PUBLIC_API_SERVER}" > .env.production
echo "NEXT_PUBLIC_WS_SERVER=ws://${BLUE_PUBLIC_API_SERVER}" >> .env.production
npm run build
npm run start
