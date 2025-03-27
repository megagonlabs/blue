#/bin/bash

# USAGE: setup_data_volume --target localhost|swarm --platform platform --data_dir directory
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
    -d|--data_dir)
      BLUE_DATA_DIR="$2"
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

# mkdirs
mkdir -p {BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/config
mkdir -p {BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/config/rbac
mkdir -p {BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/data
mkdir -p {BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/models

# copy registries
cp ${BLUE_INSTALL_DIR}/platform/setup/config/agents.json ${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/config/${BLUE_AGENT_REGISTRY}.agents.json
cp ${BLUE_INSTALL_DIR}/platform/setup/config/data.json ${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/config/${BLUE_DATA_REGISTRY}.data.json

# copy rbac
cp -r ${BLUE_INSTALL_DIR}/platform/setup/config/rbac/* ${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/config/rbac/

# copy models
cp -r ${BLUE_INSTALL_DIR}/platform/setup/models ${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}/models
