#/bin/bash

# copy rbac
mkdir -p ${BLUE_INSTALL_DIR}/platform/setup/config/rbac
cp -r ${BLUE_INSTALL_DIR}/platform/api/src/casbin/* ${BLUE_INSTALL_DIR}/platform/setup/config/rbac/

# git lfs
sudo apt-get install git-lfs
git lfs install

# sentence transformer
git clone https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2 ${BLUE_INSTALL_DIR}/platform/setup/models/paraphrase-MiniLM-L6-v2
