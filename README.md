# blue

Blue is a platform that leverages large language models (LLM) for variety of tasks that involve access to external structured data, knowledge, tools and task- and domain-specific models. The objective is to explore a design space where the LLM plays a key role but is not the 'be-all and end-all', where everything is baked into LLMs. Instead, we believe tasks can be broken down into pieces, either through recipes in a designed manner or in a decentralized but learned manner. Tasks can utilize specific models and tools, for example query structured data, extract insights, and communicate those insights to the user in natural language. As such we aimed to design a blueprint architecture that facilitates the orchestration of data and tasks, with the appopriate level of separation of concerns.

## streams
A central concept in Blue is a `stream`. A stream is essentially a sequence of data (or control instructions) that can be dynamically monitored, consumed. For example, a temperature sensor can spit out current temperature every minute to a stream. In our context, a user typing in text in a chat, asking a question can be a stream, where each token or word are transmitted as they are being typed. An LLM generating text can be another stream, and generated tokens can be output as they are being generated.

## agents
Another key concept in the blueprint architecture is an agent. An agent basically monitors to a stream, if it decides to act on it, can process the data and output into another stream. There might be yet another agent monitoring the output of the first agent and do something on top or choose to listen to the user stream. 

TODO: Add more as we make progress

## infrastructure
To run the infrastructure necessary, follow the instructions below:
```
$ cd platform
$ docker compose up
```

## v0 example
To try out demo of v0, run the following commands:
```
$ cd agents
$ python sample_user_agent.py --interactive
Starting agent USER
INFO:root:Starting producer USER
INFO:root:Streaming into USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b message {'tag': 'BOS'}
INFO:root:Streamed into USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b message {'tag': 'BOS'}
INFO:root:Started producer USER
Started agent USER
Enter Text: Hello, this is a really long message. Kidding not really.
```
Then copy the stream of the USER agent (i.e. USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b)  so that another agent listens to the user input text:
```
$ python simple_counter_agent.py --input_stream USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b
Starting agent AGENT
INFO:root:Starting producer AGENT
INFO:root:Streaming into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'BOS'}
INFO:root:Streamed into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'BOS'}
INFO:root:Started producer AGENT
INFO:root:Starting consumer AGENT
INFO:root:Creating group AGENT:3083f9cd-d223-4038-b98e-c0963fea4ddf...
INFO:root:Group info for stream USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b
INFO:root:USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b -> group name: AGENT:3083f9cd-d223-4038-b98e-c0963fea4ddf with 0 consumers and 0-0 as last read id
INFO:root:[Thread 0]: starting
INFO:root:[Thread 0]: listening... 1686093702009-0
INFO:root:[Thread 0]: listening... 1686093740505-0
INFO:root:[Thread 0]: listening... 1686093740508-0
INFO:root:[Thread 0]: listening... 1686093740511-0
INFO:root:[Thread 0]: listening... 1686093740513-0
INFO:root:[Thread 0]: listening... 1686093740516-0
INFO:root:[Thread 0]: listening... 1686093740519-0
INFO:root:[Thread 0]: listening... 1686093740521-0
INFO:root:[Thread 0]: listening... 1686093740524-0
INFO:root:[Thread 0]: listening... 1686093740526-0
INFO:root:[Thread 0]: listening... 1686093740528-0
INFO:root:[Thread 0]: listening... 1686093740531-0
['Hello,', 'this', 'is', 'a', 'really', 'long', 'message.', 'Kidding', 'not', 'really.']
INFO:root:Streaming into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'DATA', 'value': 10, 'type': 'int'}
INFO:root:Streamed into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'DATA', 'value': 10, 'type': 'int'}
INFO:root:Streaming into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'EOS'}
INFO:root:Streamed into AGENT:8b3deaea-1108-4378-a92e-0bc2a1dc7972 message {'tag': 'EOS'}
INFO:root:Stopping consumer AGENT
INFO:root:[Thread 0]: finishing
INFO:root:Started consumer AGENT
Started agent AGENT

```
In the above example, the user enters some text and another agents listens to the user stream and computes the length of the user stream and outputs that into another stream. You can see the demo stream contents using RedisInsight.

A more sophisticated example would be where an agent talks to a service over websockets. To run an example like that you first need to bring up a web service and then run the agent that talks to the service. Let's first build the service as a docker image:

```
$ cd agents/services/counter
$ ./docker_build_service.sh
```

Then run the service:
```
$ cd agents/services
$ docker compose up
```

And lastly run the agent:
```
$ cd agents
$ python websocket_counter_agent.py --input_stream USER:2e05c92d-23be-47f4-bb81-7ebbbdd0315b
```

