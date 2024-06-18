#/bin/bash
echo 'Publishing TitleRecommender Agent...'

# tag and publish
docker tag blue-agent-title_recommender:latest megagonlabs/blue-agent-title_recommender:latest
docker tag blue-agent-title_recommender:latest megagonlabs/blue-agent-title_recommender:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

docker push megagonlabs/blue-agent-title_recommender:latest
docker push megagonlabs/blue-agent-title_recommender:$(git rev-parse --abbrev-ref HEAD).$(git rev-parse --short HEAD)

echo 'Done...'
