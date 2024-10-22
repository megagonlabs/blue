#/bin/bash
echo "Deploying to localhost..."
envsubst < ${BLUE_INSTALL_DIR}/demos/employer/docker-compose-localhost-template.yaml > ${BLUE_INSTALL_DIR}/demos/employer/docker-compose-localhost-${BLUE_DEPLOY_PLATFORM}-employer.yaml
docker compose --project-directory ${BLUE_INSTALL_DIR}/demos/employer -f ${BLUE_INSTALL_DIR}/demos/employer/docker-compose-localhost-${BLUE_DEPLOY_PLATFORM}-employer.yaml -p blue_demo_employer_${BLUE_DEPLOY_PLATFORM} up -d
