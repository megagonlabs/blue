#/bin/bash

# USAGE: deploy_service --target localhost|swarm --platform platform --port_mapping port_mapping --name name --image image <positional arguments for service> <additional key=value arguments>
# if no arguments, use env variable as default

# initialize positional args
POSITIONAL_ARGS=()
ADDITIONAL_ARGS=()

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
    -m|--port_mapping)
      PORT_MAPPING="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -r|--name)
      NAME="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -i|--image)
      IMAGE="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -*|--*)
      ADDITIONAL_ARGS+="$1 $2"
      shift
      shift
      ;;
    *)
      POSITIONAL_ARGS+="$1 " 
      shift
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
echo "NAME = ${NAME}"
echo "IMAGE = ${IMAGE}"
echo "PORT_MAPPING = ${PORT_MAPPING}"

if [ $BLUE_DEPLOY_TARGET == swarm ]
then
   docker service create --mount type=volume,source=blue_${BLUE_DEPLOY_PLATFORM}_data,destination=/blue_data --network blue_platform_${BLUE_DEPLOY_PLATFORM}_network_overlay --hostname blue_service_${NAME} --constraint node.labels.target==service ${IMAGE} ${POSITIONAL_ARGS} ${ADDITIONAL_ARGS}
elif [ $BLUE_DEPLOY_TARGET == localhost ]
then
   docker run -d --volume=blue_${BLUE_DEPLOY_PLATFORM}_data:/blue_data --network=blue_platform_${BLUE_DEPLOY_PLATFORM}_network_bridge --hostname blue_service_${NAME} -p ${PORT_MAPPING}  ${IMAGE} ${POSITIONAL_ARGS} ${ADDITIONAL_ARGS}
fi
