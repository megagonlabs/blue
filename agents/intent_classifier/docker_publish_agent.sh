#/bin/bash
echo 'Publishing Intent Classifier Agent...'

# tag and publish
docker tag blue-agent-intent_classifier:latest megagonlabs/blue-agent-intent_classifier:latest
docker tag blue-agent-intent_classifier:latest megagonlabs/blue-agent-intent_classifier:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-intent_classifier:latest
docker push megagonlabs/blue-agent-intent_classifier:$(git rev-parse --abbrev-ref HEAD)-$(git rev-parse --short HEAD)

echo 'Done...'
