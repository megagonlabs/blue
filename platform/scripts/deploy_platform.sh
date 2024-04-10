#/bin/bash

# USAGE: deploy_platform --target localhost|swarm --platform platform --api_server address:port
# if no arguments, use env variable as default

while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--target)
      BLUE_DEPLOY_TARGET="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -p|--platform)
      BLUE_DEPLOY_PLATFORM="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -a|--api_server)
      BLUE_PUBLIC_API_SERVER="$2"
      # pass argument and value
      shift
      shift
      ;;
    -*|--*)
      echo "Unknown argument: $1"
      exit 1
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# set target to local, if not provided
if [ -z "$BLUE_DEPLOY_TARGET" ]
then
   export BLUE_DEPLOY_TARGET=localhost
fi

# set platform to default, if not provided
if [ -z "$BLUE_DEPLOY_PLATFORM" ]
then
   export BLUE_DEPLOY_PLATFORM=default
fi

echo "DEPLOY TARGET   = ${BLUE_DEPLOY_TARGET}"
echo "DEPLOY PLATFORM = ${BLUE_DEPLOY_PLATFORM}"
echo "BLUE_INSTALL_DIR = ${BLUE_INSTALL_DIR}"

if [ $BLUE_DEPLOY_TARGET == swarm ]
then
   envsubst < ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-template.yaml > ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-${BLUE_DEPLOY_PLATFORM}.yaml
   docker stack deploy -c ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-${BLUE_DEPLOY_PLATFORM}.yaml blue_platform_${BLUE_DEPLOY_PLATFORM}
elif [ $BLUE_DEPLOY_TARGET == localhost ]
then
   envsubst < ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-template.yaml > ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-${BLUE_DEPLOY_PLATFORM}.yaml
   docker compose --project-directory ${BLUE_INSTALL_DIR}/platform -f ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-${BLUE_DEPLOY_PLATFORM}.yaml -p blue_platform_${BLUE_DEPLOY_PLATFORM} up -d
fi
