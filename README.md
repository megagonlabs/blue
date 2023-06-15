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

Let's dive into a bit of development of the agents. The `agents/shared_lib` contains an Agent class that can be used as a base class for developing new agents. You do not necessarily need to extend the base class to create a new class for an agent as you can use the Agent class directly, and use the APIs to process data from other agents. Let's go through an example that basically uses base class:

```
# create a user agent
    user_agent = Agent("USER")
    session = user_agent.start_session()

    # sample func to process data for counter
    stream_data = []

    def processor(id, event, value):
        if event == 'EOS':
            # print all data received from stream
            print(stream_data)

            # compute stream data
            l = len(stream_data)
            time.sleep(4)
            
            # output to stream
            return l
           
        elif event == 'DATA':
            # store data value
            stream_data.append(value)
    
        return None

    # create a counter agent in the same session
    counter_agent = Agent("COUNTER", session=session, processor=processor)

    # user initiates an interaction
    user_agent.interact("hello world!")

    # wait for session
    session.wait()
```

In the above example, a `USER` agent is created and `create_session` function on the Agent is called to create a Session object. That session object is passed to another Agent, called `COUNTER`, along with a `processor` function to process data in the `COUNTER` agent. 

The signature of the `processor` function is `id`, `event`, and `value`. `id` is the data id assigned (by Redis) stream. `event` is the type of data in the stream, for example `BOS` for beginning of stream, `EOS` for end of stream, `DATA` for a data in stream. Essentially above `processor` function adds new data to `stream_data` when it receives new data (e.g. on `DATA` event) and returns count when all data is received (e.g. on `EOS` event). The base class `Agent` automatically creates a new stream in the session and adds the returned value from the stream so that other agents might start listening to new streams and data in the session.

In the end, upon running the above code the streams in the session will be:

| SESSION:493e2083-61a0-4c90-accf-3d372f5b8aac                   |
| ---------------------------------------------------------------|
| event: BOS                                                     | 
| event: ADDS, data: USER:c124ca2b-6602-4bdf-882e-f45518d30c85   |
| event: ADDS, data: COUNTER:44d7b977-eb7f-4d7f-8c33-8b3d2b11c3c2|

| USER:c124ca2b-6602-4bdf-882e-f45518d30c85 |
|-------------------------------------------|
| event: BOS                                |
| event: DATA, data: hello, type: str       |
| event: DATA, data: world!, type: str      |
| event: EOS                                |

| COUNTER:44d7b977-eb7f-4d7f-8c33-8b3d2b11c3c2 | 
|----------------------------------------------|
| event: BOS                                   |
| event: DATA, data: 2, type: int              |
| event: EOS                                   |

First stream refers to session stream, basically all events happening in the session, specifically when a new stream is generated by an agent, all others can get which stream is generated and who generated it.

Second stream refers to the output from the `USER` stream, essentially the text entered: `hello` and `world!`

Third stream refers to the output from the `COUNTER` stream, essentially the count of the tokens in the `USER` stream, as processed and returned by the agent.

That is it!

Not quite. One question is who is listening to who. At the moment all agents listen to all streams produced by agents, except themselves. This and many more orchestration of work related design and implementation will come in the next few weeks.

That is it, for now. :) 



