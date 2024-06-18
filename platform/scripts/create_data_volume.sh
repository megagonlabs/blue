#/bin/bash

# USAGE: create_data_volume --target localhost|swarm --platform platform --data_dir directory
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

mkdir -p ${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM}
docker volume create --driver local  --opt type=none --opt device=${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM} --opt o=bind blue_${BLUE_DEPLOY_PLATFORM}_data
