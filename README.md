# blue

Blue is a platform that leverages large language models (LLM) for variety of tasks that involve access to external structured data, knowledge, tools and task- and domain-specific models. The objective is to explore a design space where the LLM plays a key role but is not the 'be-all and end-all', where everything is baked into LLMs. Instead, we believe tasks can be broken down into pieces, either through recipes in a designed manner or in a decentralized but learned manner. Tasks can utilize specific models and tools, for example query structured data, extract insights, and communicate those insights to the user in natural language. As such we aimed to design a blueprint architecture that facilitates the orchestration of data and tasks, with the appopriate level of separation of concerns.

## streams
A central concept in Blue is a `stream`. A stream is essentially a sequence of data (or control instructions) that can be dynamically monitored, consumed. For example, a temperature sensor can spit out current temperature every minute to a stream. In our context, a user typing in text in a chat, asking a question can be a stream, where each token or word are transmitted as they are being typed. An LLM generating text can be another stream, and generated tokens can be output as they are being generated.

## agents
Another key concept in the blueprint architecture is an agent. An agent basically monitors to a stream, if it decides to act on it, can process the data and output into another stream. There might be yet another agent monitoring the output of the first agent and do something on top or choose to listen to the user stream. 

TODO: Add more as we make progress

## requirements
Blue requires docker engine to build and run the infrastruture and agents. To develop on your local machine you would need to install docker enginer from 
https://docs.docker.com/engine/install/

## infrastructure
To run the infrastructure necessary, follow the instructions below:
```
$ cd platform
$ docker compose up
```

## v0.1 example
To try out demo of v0.1, run the following commands:
```
$ cd agents/simple_user
$ python src/simple_user_agent.py --interactive
[...]
INFO:root:Started consumer USER for stream SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac
Enter Text: Hello, this is a really long message. Kidding not really.
```
Then copy the session the USER agent created (i.e. SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac)  so that another agent can participate in the same session:
```
$ cd agents/simple_counter
$ python src/simple_counter_agent.py --session SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac
[...]
```
In the above example, the user enters some text and another agents listens to the sesssion the user agent works in, when the user agent creates a stream and enter text, the counter agent above picks up the stream and computes the length of the user stream and outputs that into another stream in the session.. You can see the demo stream contents using RedisInsight.

A more sophisticated example would be where an agent talks to a service over websockets. To run an example like that you first need to bring up a web service and then run the agent that talks to the service. Let's first build the service as a docker image:

```
$ cd agents/websocket_counter
$ ./docker_build_service.sh
```

Then run the service:
```
$ cd agents/websocker_counter
$ docker compose up
```

And lastly run the agent:
```
$ cd agents/websocket_counter
$ python src/websocket_counter_agent.py --session SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac
```

As a matter of fact, not just the services for the agents, the agents themselves can also be run in a dockerized manner. To do so, run the `docker_build_agent.sh` in the respective agents folders. This should be docker images such as `blue-agent-websocket_counter`, which you can list using `docker image ls`, for example.

To run dockerized version of the agents you would need to run `docker run` commands with the image names and parameters. For example, the agents in v0.1 examples can be as below:
```
$ docker run -e text="this is a different text" --network="host" blue-agent-simple_user
$ docker run -e session=SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac --network="host" blue-agent-simple_counter
$ docker run -e session=SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac --network="host" blue-agent-websocket_counter
```

## development

TODO:

