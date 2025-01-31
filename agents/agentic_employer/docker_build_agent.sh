#/bin/bash
echo 'Building docker image...'

# build docker
docker build --no-cache -t blue-agent-agentic_employer:latest -f Dockerfile.agent .

# tag image
docker tag blue-agent-agentic_employer:latest blue-agent-agentic_employer:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
