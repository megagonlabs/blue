#/bin/bash

# USAGE: shutdown_platform --target localhost|swarm --platform platform
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
   export BLUE_DEPLOY_TARGET=local
fi

# set platform to default, if not provided
if [ -z "$BLUE_DEPLOY_PLATFORM" ]
then
   export BLUE_DEPLOY_PLATFORM=default
fi

echo "DEPLOY TARGET   = ${BLUE_DEPLOY_TARGET}"
echo "DEPLOY PLATFORM = ${BLUE_DEPLOY_PLATFORM}"

if [ $BLUE_DEPLOY_TARGET == swarm ]
then
   docker stack rm blue_platform_${BLUE_DEPLOY_PLATFORM}
elif [ $BLUE_DEPLOY_TARGET == localhost ]
then
   docker compose --project-directory ${BLUE_INSTALL_DIR}/platform -f docker-compose-localhost.yaml -p blue_platform_${BLUE_DEPLOY_PLATFORM} down 
fi
