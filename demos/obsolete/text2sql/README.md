# TEXT2SQL

This demo illustrates our work on text to sql generation. 


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
Invoke user agent to input text to be translated into SQL:
```
$ ./user.sh 'all cities in the world'
```

 Retrieve the `SESSION_ID` from logs of the user agent on system output, or using:
```
docker logs -f <docker_id>
```
Or, alternatively you can also retrieve it from the Redis Stream

### observer.sh
To observe the outputs from each agent run observer agent using the session is from the output of user.sh script:
```
$ ./observer.sh <SESSION_ID>
```

### sqlforge.sh

To translate user query into SQL, run:
```
$ ./sqlforge.sh <SESSION_ID>
```

### Cleanup
Once the demo is done you can stop all agents using `stop_agents.sh` and all agent services using `stop_agent_services.sh`.
To stop platform:
```
$ cd platform
$ ./stop.sh
```