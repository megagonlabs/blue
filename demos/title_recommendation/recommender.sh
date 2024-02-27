docker rm blue_agent_title_recommender
# TitleReommender Agent
echo "Bring up TITLERECOMMENDER agent:"
docker run  -d --network="host" --name blue_agent_title_recommender blue-agent-title_recommender:latest --session $1
