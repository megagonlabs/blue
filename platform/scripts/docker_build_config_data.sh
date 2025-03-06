#/bin/bash

# USAGE: docker_build_config_data --platform platform 
# if no arguments, use env variable as default

while [[ $# -gt 0 ]]; do
  case $1 in
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

# set platform to default, if not provided
if [ -z "$BLUE_DEPLOY_PLATFORM" ]
then
   export BLUE_DEPLOY_PLATFORM=default
fi

echo "DEPLOY PLATFORM = ${BLUE_DEPLOY_PLATFORM}"

# create dummy container to copy files to volume
docker run -d --rm --name dummy alpine tail -f /dev/null

# copy registry defaults
docker exec dummy mkdir /mnt/config
docker exec dummy mkdir /mnt/data
docker exec dummy mkdir /mnt/models
docker cp ${BLUE_INSTALL_DIR}/platform/cli/blue_cli/configs/agents.json dummy:/mnt/config/${BLUE_DEPLOY_PLATFORM}.agents.json
docker cp ${BLUE_INSTALL_DIR}/platform/cli/blue_cli/configs/data.json dummy:/mnt/config/${BLUE_DEPLOY_PLATFORM}.data.json
docker cp ${BLUE_INSTALL_DIR}/platform/cli/blue_cli/configs/models.json dummy:/mnt/config/${BLUE_DEPLOY_PLATFORM}.models.json
docker cp ${BLUE_INSTALL_DIR}/platform/cli/blue_cli/configs/operators.json dummy:/mnt/config/${BLUE_DEPLOY_PLATFORM}.operators.json
# copy rbac
docker exec dummy mkdir /mnt/config/rbac
docker cp ${BLUE_INSTALL_DIR}/platform/api/src/casbin/model.conf dummy:/mnt/config/rbac/
docker cp ${BLUE_INSTALL_DIR}/platform/api/src/casbin/policy.csv dummy:/mnt/config/rbac/

# temporary directory for model
mkdir -p ${BLUE_INSTALL_DIR}/models/

# clone models
git clone https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2 ${BLUE_INSTALL_DIR}/models/paraphrase-MiniLM-L6-v2
docker cp ${BLUE_INSTALL_DIR}/models/ dummy:/mnt/

# commit
docker commit dummy ${BLUE_CORE_DOCKER_ORG}/blue-config-data:${BLUE_DEPLOY_VERSION}

# publish
docker push ${BLUE_CORE_DOCKER_ORG}/blue-config-data:${BLUE_DEPLOY_VERSION}

# remove dummy container
docker rm --force dummy
