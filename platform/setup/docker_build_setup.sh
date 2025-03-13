#/bin/bash
echo "Building docker image ..."
echo "${BLUE_CORE_DOCKER_ORG}/blue-platform-api:${BLUE_DEPLOY_VERSION}"
echo "plaforms: ${BLUE_BUILD_PLATFORM}"

# copy rbac
mkdir -p ${BLUE_INSTALL_DIR}/platform/setup/config/rbac
cp -r ${BLUE_INSTALL_DIR}/platform/api/src/casbin/* ${BLUE_INSTALL_DIR}/platform/setup/config/rbac/

# git lfs
sudo apt-get install git-lfs
git lfs install

# sentence transformer
git clone https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2 ${BLUE_INSTALL_DIR}/platform/setup/models/paraphrase-MiniLM-L6-v2

# build docker
docker buildx build --platform ${BLUE_BUILD_PLATFORM} --no-cache --push -t ${BLUE_CORE_DOCKER_ORG}/blue-platform-setup:${BLUE_DEPLOY_VERSION} -f Dockerfile.setup .

echo 'Done...'
