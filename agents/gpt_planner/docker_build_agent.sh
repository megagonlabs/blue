#/bin/bash
echo 'Building GPT Planner Agent...'

# cleanup libs
rm -r lib

# copy from agent lib
mkdir -p lib/agent; cp -r ../lib/* lib/agent/

# copy from api agent lib
mkdir -p lib/apicaller; cp -r ../api/src/* lib/apicaller/

# copy from openai agent lib
mkdir -p lib/openai; cp -r ../openai/src/* lib/openai/

# copy from platform lib
mkdir -p lib/platform; cp -r ../../platform/lib/* lib/platform/

# copy from agent_registry lib
mkdir -p lib/agent_registry; cp -r ../../platform/agent_registry/src/* lib/agent_registry/

# copy from utils shared lib
mkdir -p lib/utils; cp -r ../../utils/lib/* lib/utils/

# build docker
docker build -t blue-agent-gpt_planner:latest -f Dockerfile.agent .
echo 'Done...'
