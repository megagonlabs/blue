#/bin/bash
echo 'Publishing TripleExtractor Agent...'

# tag and publish
docker tag blue-agent-triple_extractor:latest megagonlabs/blue-agent-triple_extractor:latest
docker tag blue-agent-triple_extractor:latest megagonlabs/blue-agent-triple_extractor:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-triple_extractor:latest
docker push megagonlabs/blue-agent-triple_extractor:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
