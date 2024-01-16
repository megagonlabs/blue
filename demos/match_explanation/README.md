# Match Explanation

This demo illustrates a number of agents working together to explain a match of a resume to a corresponding job description. 

Overall the demo illustrates:
* Ability to fetch structured data (e.g. query neo4j, postgres) from a data lake [API/STRUCTURED DATA]

## Running the Demo

### Build Platform

```
$ cd platform
$ ./start.sh
```

### Set BLUE_INSTALL_DIR

Set the `$BLUE_INSTALL_DIR` to your local path where the blue repo has been installed.

```
$ echo "export BLUE_INSTALL_DIR='<path_to_blue_dir>'" >> ~/.zshrc
```

### flush.sh
To flush the contents of the Redis backend run:
```
$ ./flush.sh
```

### user.sh
Invoke user agent to input text:
```
$ ./user.sh 'Using the information from the resume of Kushan Mitra recommend a title for him'
```

 Run the following command and retrieve `SESSION_ID` from the docker logs which states "...streamed into session <SESSION_ID>"
```
docker logs -f <docker_id>
```
Or, alternatively you can also retrieve it from the Redis Stream

### observer.sh
To observe the outputs from each agent run observer agent using the session is from the output of user.sh script:
```
$ ./observer.sh <SESSION_ID>
```

### openai.sh

Set your `OPENAI_API_KEY` in `agents/openai/openai.env`

Next, run a few agents to detect explicit information need (e.g. resume of Kushan) and convert it into a query (CYPHER):
```
$ ./openai.sh <SESSION_ID>
```

### neo4j.sh

Set environment variables `NEO4J_USER`, `NEO4J_PWD` and `NEO4J_HOST`.

Then, run agent to execute CYPHER queries and fetch the results:
```
$ ./neo4j.sh <SESSION_ID>
```

### recorder.sh
To scan JSON output from a number of agents and record in session memory:
```
$ ./recorder.sh <SESSION_ID>
```

### recommender.sh
Given a title in memory run a recommeder for next title:
```
$ ./recommender.sh <SESSION_ID>
```

### kgr.sh
Given a title recommendation, ground the information gap to rationalize the result, pull in additional information, and summarize/rationalize the result:
```
$ ./kgr.sh <SESSION_ID>
```

### Cleanup
Once the demo is done you can stop all agents using `stop_agents.sh` and all agent services using `stop_agent_services.sh`.
To stop platform:
```
$ cd platform
$ ./stop.sh
```

