docker rm blue_agent_recorder
# Recorder Agent
export RECORDER_PROPERTIES='{"records":[{"variable":"title","single":true,"query":"$[0]['res']['current_title']"},{"variable":"top_title_recommendation","single":true,"query":"$['title_recommendations'][1]"},{"variable":"name","single":true,"query":"$[0]['p']['name']"},{"variable":"resume_skills","single":true,"query":"$['resume_skills']"},{"variable":"top_title_skills","single":true,"query":"$['top_title_skills']"}]}'
echo "Bring up RECORDER agent using the following properties: $RECORDER_PROPERTIES"
docker run  -d --network="host" --name blue_agent_recorder blue-agent-recorder:latest --session $1 --properties "$RECORDER_PROPERTIES"
