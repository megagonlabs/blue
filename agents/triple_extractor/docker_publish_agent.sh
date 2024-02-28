#/bin/bash
echo 'Publishing TripleExtractor Agent...'

# tag and publish
docker tag blue-agent-triple_extractor:latest megagonlabs/blue-agent-triple_extractor:latest
docker push megagonlabs/blue-agent-triple_extractor:latest

echo 'Done...'
