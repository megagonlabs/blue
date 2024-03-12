#/bin/bash

# USAGE: deploy_agent --target localhost|swarm --platform platform --registry registry --agent agent --image image <positional arguments for agent>
# if no arguments, use env variable as default

# initialize positional args
POSITIONAL_ARGS=()

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
    -r|--registry)
      REGISTRY="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -a|--agent)
      AGENT="$2"
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
      echo "Unknown argument: $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+="$1 " 
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

# set registry to default, if not provided
if [ -z "$REGISTRY" ]
then
   export REGISTRY=default
fi

echo "DEPLOY TARGET   = ${BLUE_DEPLOY_TARGET}"
echo "DEPLOY PLATFORM = ${BLUE_DEPLOY_PLATFORM}"
echo "REGISTRY = ${REGISTRY}"
echo "AGENT = ${AGENT}"
echo "IMAGE = ${IMAGE}"

if [ $BLUE_DEPLOY_TARGET == swarm ]
then
   docker service create --mount type=volume,source=blue_data,destination=/blue_data --network blue_platform_${BLUE_DEPLOY_PLATFORM}_network_overlay --hostname blue_agent_${REGISTRY}_${AGENT} --constraint node.labels.target==agent ${IMAGE} --serve ${POSITIONAL_ARGS}
elif [ $BLUE_DEPLOY_TARGET == localhost ]
then
   docker run -d --volume=blue_data:/blue_data --network=blue_platform_${BLUE_DEPLOY_PLATFORM}_network_bridge --hostname blue_agent_${REGISTRY}_${AGENT} ${IMAGE} --serve ${POSITIONAL_ARGS}
fi
