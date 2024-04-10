#/bin/sh
echo "NEXT_PUBLIC_API_SERVER=$BLUE_PUBLIC_API_SERVER" > .env.production
echo "NEXT_PUBLIC_WS_SERVER=$BLUE_PUBLIC_WS_SERVER" >> .env.production
npm run build
npm run start
