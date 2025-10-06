#/bin/bash
# ray
cd ${BLUE_INSTALL_DIR}/platform/ray
./docker_build_ray.sh
# api
cd ${BLUE_INSTALL_DIR}/platform/api
./docker_build_api.sh
# frontend
cd ${BLUE_INSTALL_DIR}/platform/frontend
./docker_build_frontend.sh
