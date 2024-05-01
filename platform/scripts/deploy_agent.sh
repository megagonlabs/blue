#/bin/bash

# USAGE: deploy_agent --target localhost|swarm --platform platform --registry registry --agent agent --image image <positional arguments for agent> <additional key=value arguments>
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
      ADDITIONAL_ARGS+="$1=$2"
      shift
      shift
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

export ADDITIONAL_ARGS=${ADDITIONAL_ARGS}
export POSITIONAL_ARGS=${POSITIONAL_ARGS}
export IMAGE=${IMAGE}
export AGENT=${AGENT}
export AGENT_LOWERCASE=$(echo ${AGENT}| tr '[:upper:]' '[:lower:]')

echo "DEPLOY TARGET  = ${BLUE_DEPLOY_TARGET}"
echo "DEPLOY PLATFORM = ${BLUE_DEPLOY_PLATFORM}"
echo "REGISTRY = ${REGISTRY}"
echo "AGENT = ${AGENT}"
echo "AGENT_LOWERCASE = ${AGENT_LOWERCASE}"
echo "IMAGE = ${IMAGE}"


if [ $BLUE_DEPLOY_TARGET == swarm ]
then
   envsubst < ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-agent-template.yaml > ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-agent-${BLUE_DEPLOY_PLATFORM}-${REGISTRY}-${AGENT}.yaml
   docker stack deploy -c ${BLUE_INSTALL_DIR}/platform/docker-compose-swarm-agent-${BLUE_DEPLOY_PLATFORM}-${REGISTRY}-${AGENT}.yaml blue_agent_${REGISTRY}_${AGENT_LOWERCASE}
elif [ $BLUE_DEPLOY_TARGET == localhost ]
then
   envsubst < ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-agent-template.yaml > ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-agent-${BLUE_DEPLOY_PLATFORM}-${REGISTRY}-${AGENT}.yaml
   docker compose --project-directory ${BLUE_INSTALL_DIR}/platform -f ${BLUE_INSTALL_DIR}/platform/docker-compose-localhost-agent-${BLUE_DEPLOY_PLATFORM}-${REGISTRY}-${AGENT}.yaml -p blue_agent_${REGISTRY}_${AGENT_LOWERCASE} up -d
fi


