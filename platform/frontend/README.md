# frontend 

Blue platform supports a web interface through which you can interact with the system. 

## build

To build the frontend:
```
$ cd platform/frontend
$  ./docker_build_frontend.sh
```
## deploy

Frontend is deployed as part of the overall platform.
```
$ cd platform/scripts
$ ./deploy_platform.sh
```

## run

Frontend is developed using [Next.js](https://nextjs.org/) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

To run it locally during development:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result on your localhost.

