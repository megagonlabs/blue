# Agents

Below you will find more information on developing your own agents as well as a list of generic agents that you can learn from and use as a template.

Use below links for quick accces:
* [agent development](#agent-development)
* [template agent](#template-agent)
* [generic agents](#generic-agents)

</br>
</br>

---

## agent development

Let's dive into a bit of development of the agents. 

The `agents/lib` contains an Agent class that can be used as a base class for developing new agents. However, you do not necessarily need to extend the base class as you can simply use the Agent class directly. 

Let's go through an example that basically uses base class. You can find this example in `agents/test` directory. To setup for this example:

```
$ cd agents/python
$ pip install -r requirements.txt
$ ./build_agent.sh
```

[Developers Note: Use above approach until we have released a blue python library]. 

Then, invoke a python interpreter (in `agents/test`):
```
$ python
```

First, to import Agent class, `import sys` so that you can access classes defined in various directories under `lib`. Afterwards, import `Agent` and `Session`:
```
import sys

sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')

from agent import Agent
from session import Session
```

In this example, let's first create a USER agent by simply using the existing Agent class, then start a session, and input some text using the `interact` function of the Agent class.
```
# create a user agent
user_agent = Agent("USER")
session = user_agent.start_session()

# user initiates an interaction
user_agent.interact("hello world!")
```
If you examine the logs (see below), you will see that we create a new stream `USER:275e2d0b` with `BOS` (begin-of-stream) and then put two `DATA` messages into the stream corresponding to the input text, and ended the stream with `EOS` (end-of-stream).

```
INFO:root:Streamed into USER:275e2d0b message {'label': 'BOS'}
[...]
INFO:root:Streamed into USER:275e2d0b message {'label': 'DATA', 'data': 'hello', 'type': 'str'}
INFO:root:Streamed into USER:275e2d0b message {'label': 'DATA', 'data': 'world!', 'type': 'str'}
INFO:root:Streamed into USER:275e2d0b message {'label': 'EOS'}
```

Now, let's create a COUNTER agent, again using the base Agent class. The counter agent will listen to the streams in the same session as the USER agent (Note session=session in the initializer of the agent, where session is created above by the USER agent). Then we define a `processor` function to process stream data.

The signature of the `processor` function is `stream`, `id`, `label`, and `data`. `stream` is the input stream to process, `id` is the data id assigned stream. `label` is the label of message in the stream, for example `BOS` for begin-of-stream, `EOS` for end-of-stream, `DATA` for a data in stream. Essentially, above `processor` function adds new data to `stream_data` when it receives new data (e.g. on `DATA` label) and returns count when all data is received (e.g. on `EOS` label). The base class `Agent` automatically creates a new stream in the session and adds the returned value from the processor function.


```
# sample func to process data for counter
stream_data = []

def processor(stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
    if label == 'EOS':
        # print all data received from stream
        print(stream_data)
        # compute stream data
        l = len(stream_data)
        # output to stream
        return l 
    elif label == 'DATA':
        # store data value
        stream_data.append(data)
        return None

# create a counter agent in the same session
counter_agent = Agent("COUNTER", session=session, processor=processor)
```

Now, this time if you examine the logs you will see:
```
[...]
INFO:root:Streamed into COUNTER:5f1fa5a5 message {'label': 'DATA', 'data': 2, 'type': 'int'}
[...]
```

In addition if you examine the session stream, you will see:

```
| SESSION:5db16fd4                                                                   |
| -----------------------------------------------------------------------------------|
| label: BOS                                                                         | 
| label: JOIN, data: {"agent": "USER"}, type: JSON                                   | 
| label: ADD, data: {"stream": "USER:8d29992c", "tags": ["USER"]}, type: JSON        |
| label: JOIN, data: {"agent": "COUNTER"}, type: JSON                                | 
| label: ADD, data: {"stream": "COUNTER:5f1fa5a5", "tags": ["COUNTER"]}, type: JSON  |
```

This basically illustrates the session mechanism. When an agents starts a session, a new session stream (`SESSION:5db16fd4`) is started. Then we see a `JOIN` event and agent `USER` joined the session, and it created a new stream `USER:8d29992c`. In a way the session stream announced that there is new data in the session, produced by the `USER` agent. Then, later we see another `JOIN` event and agent `COUNTER` joined the session, and it later created a new stream `COUNTER:5f1fa5a5` upon listening and processing data from the `USER` agent in `USER:8d29992c` stream.

So, you might ask how did the `COUNTER` agent listened to `USER` agent. Each agent joining the session listens to all events in the session stream, and start keeping track of `ADD` events where new data is introduced into the session. As you see above along with each stream there are `tags`, for example stream `USER:8d29992c` is tagged as `USER`.

To decide which agents to listen to agents (actually more like streams), each agent defines a `listens` property and `includes` and `excludes` list. 

Basically, agents tag each stream they produce, as you have seen above, `USER` agent tagged its output stream as `USER`. Other agents in the session check if their `includes` and `excludes` list against the tags of the stream. Agents by default tag each stream they produce by their own name. Additional, tags can be provided as a property (`tags`).  `includes` and `excludes` lists are ordered lists of regular expressions that are evaluated on stream tags (e.g. USER, ). To decide if an agents should be listened to first the `includes` list is processed. If none of the regular expressions is matched, the stream with the tags is not listened to. If any of the regular expressions is a match, a further check is made in the `excludes` list. If none of the `excludes` regular expressions is matched the stream is listened. If any one of `excludes` is matched the stream is not listened to. Default `includes` list is ['.*'], i.e. all agents are listened to, and the default `excludes` list is `[self.name]`, i.e. self is not listened to. Both include and exclude list can include an element that is itself a list, e.g. `["A","B",["C","D"]]` to support conjunctions. For example, previous example is `A or B or (C and D)`.


## memory 
The above example works if there is only one worker and that worker is solely responsible from start to end (i.e. it doesn't fail). The reason is that in the above example `stream_data` is a shared variable among all workers of the agent, even when they work on a different stream. To resolve this issue, you need to create distributed memory (uses Redis JSON) that a worker can write its private data that is only specific to a stream. 

As discussed earlier there are three scopes of shared memory. Below are API functions for reading and writing in these respective scopes. To allow this you will use the worker that is passed on as a keyword parameter to the processor function, i.e. 
```
def processor(stream, id, label, data, worker=None):
```

and use the following worker functions to write data:

For private worker/stream you can call the following functions on the keyword parameter `worker`, `set_data(key, value)`, `append_data(key, value)`, `get_data(key)`, and `get_data_len(key)`. For example, worker.set_data('a', 3), and worker.get_data('a'). The value can be any JSON value. 

To share data among workers from the same agent, you can use `set_agent_data(key, value)`, `append_agent_data(key, value)`, `get_agent_data(key)`, and `get_agent_data_len(key)`.

To share data among workers processing data from the same stream, you can use `set_stream_data(key, value)`, `append_stream_data(key, value)`, `get_stream_data(key)`, and `get_stream_data_len(key)`.

To share data among all agent works in the session, you can use `set_session_data(key, value)`, `append_session_data(key, value)`, `get_session_data(key)`, and `get_session_data_len(key)`.


</br>
</br>

---

## template agent

Key functionality of the agent is defined in the `processor` function, the rest is template. To help develop agents you can use the `agents/template` code as starter code.
</br>
</br>

---

## generic agents

Below is a list of agents that you can directly use as they are generic. Also look for other agents in `agents` directory to use them as examples.

* [API Caller Agent](apicaller)
* [OpenAI Agent](openai)
