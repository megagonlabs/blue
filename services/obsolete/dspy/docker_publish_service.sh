#/bin/bash
echo 'Publishing DSPy Service...'

# tag and publish
docker tag blue-service-dspy:latest megagonlabs/blue-service-dspy:latest
docker tag blue-service-dspy:latest megagonlabs/blue-service-dspy:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-service-dspy:latest
docker push megagonlabs/blue-service-dspy:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
