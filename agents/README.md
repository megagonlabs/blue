# Agents

Below you will find more information on developing your own agents as well as a list of generic agents that you can learn from and use as a template.

Use below links for quick accces:
- [Agents](#agents)
  - [agent development](#agent-development)
  - [memory](#memory)
  - [interactive agents](#interactive-agents)
  - [template agent](#template-agent)
  - [template interactive agent](#template-interactive-agent)
  - [generic agents](#generic-agents)

</br>
</br>

---

## agent development

Let's dive into a bit of development of the agents. 

The `agents/lib` contains an Agent class that can be used as a base class for developing new agents. While it is often the practice to use Agent class as the base class, however, you do not necessarily need to extend the base class as you can simply use the Agent class directly, and pass in different parameters (e.g. processor).

Let's go through an example that basically uses Agent class directly. You can find this example in `agents/test` directory. To setup for this example:

```
$ cd agents/python
$ pip install -r requirements.txt
$ ./build_agent.sh
```

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

In this example, let's first create a session, then have a USER agent, simply using the existing Agent class,  input some text using the `interact` function of the Agent class.
```
# create a session
session = Session()

# create a user agent
user_agent = Agent(name="USER", session=session)

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

Now, let's create a COUNTER agent, again using the base Agent class. The counter agent will listen to the streams in the same session as the USER agent. Then, we define a `processor` function to process stream data.

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
label: INSTRUCTION, data: {"code": "ADD_STREAM", "params": {"cid": "COUNTER:b55fdf56:STREAM:c80f0769", "tags": ["COUNTER"]}}, type: JSON
label: INSTRUCTION, data: {"code": "ADD_AGENT", "params": {"name": "COUNTER", "sid": "COUNTER:b55fdf56"}}, type: JSON
label: INSTRUCTION, data: {"code": "ADD_STREAM", "params": {"cid": "USER:9ccad900:STREAM:b15675db", "tags": ["USER"]}}, type: JSON
label: INSTRUCTION, data: {"code": "ADD_AGENT", "params": {"name": "USER", "sid": "USER:9ccad900"}}, type: JSON
```

This basically illustrates the session mechanism. When an session is created, a new session stream (`SESSION:5db16fd4`) is started. Then we see a `ADD_AGENT` instruction and agent `USER` joined the session, and it created a new stream `USER:8d29992c` and announced via the `ADD_STREAM` instruction, etc. In a way the session stream announced that there is new agent and new data in the session, produced by the `USER` agent. Then, later we see similar instructions for the `COUNTER` agent.

So, you might ask how did the `COUNTER` agent listened to `USER` agent. Each agent joining the session listens to all events in the session stream, and start monitoring `ADD_STREAM` instructions where new data is introduced into the session. As you see above along with each stream there are `tags`, for example stream `USER:9ccad900:STREAM:b15675db` is tagged as `USER`.

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

To share data among workers processing data from the same stream, you can use `set_stream_data(key, value)`, `append_stream_data(key, value)`, `get_stream_data(key)`, and `get_stream_data_len(key)`.

To share data among all agent workers in the session, you can use `set_session_data(key, value)`, `append_session_data(key, value)`, `get_session_data(key)`, and `get_session_data_len(key)`.


## interactive agents
Building interactive agents, i.e. agents that present the user an interface, for example a form to fill out, is possible through a declarative UI specification. In blue we use [JSONForms](https://jsonforms.io/) to facilitate that. Essentially the agent in its reponses sends back a form that describes the ui layout and data schema.  The web interface renders it accordingly. Along with the form, and event stream is created, where the `processor` of the agent can start consuming event from the web interface. The interactive agent then can send more messages, new user interfaces, or other events that changes the UI, accordingly. 

To support interactive agent development in the web interface there is a Form Designer tool that allows you to design ui and data schemas in an interactive manner, along with the documentation. 

Assuming you now have worked out the uischema (e.g. form design) and schema (e.g. data structure), the main difference of an interactive widget is what is returned from the `processor` function. To return a UI, simply return:
`("INTERACTION", {"type": "JSONFORM", "content": form}, "json", False)` where form is a JSON object with `uischema` and `schema` as its contents (from the Form Designer).

To process events from the web interface, as the user interacts, you can check the `stream` parameter of the `processor` function. Event messages come from a stream with `<prefix>:EVENT_MESSAGE:<form>`, where `<prefix>` is the output stream of the interactive agent, and `<form>` is the form id of the form events are received from. Typically, events as `DATA` with the contents describing the target widget and values, e.g.:
`{"name_id": "desired_location", "form_id": "90d46b5e", "value": "mountain view, ca", "timestamp": 1718124950421}`, where
`name_id` is the name of the widget, `form_id` is the id of the form, and `value` is the current value of the widget. The processor, then does whathever is necessary to handle the event, as this part is application logic dependent. The widget can be disabled by sending `("INTERACTION",{"type": "DONE", "form_id": <form_id>}, "json")`.

</br>
</br>

---

## template agent

Key functionality of the agent is defined in the `processor` function, the rest is template. To help develop agents you can use the [template agent](template) code as starter code.
</br>
</br>

---

## template interactive agent

See the `processor` function in the template interactive agent to see how to send interactive forms to render on the web application. To help develop interactive agents you can use the [template-interactive agent](template-interactive) code as starter code.

Build interactive forms using "Form Designer" in the "Dev. Tools" section of the navigation menu. Instructions on the form elements are available within the interface.
</br>
</br>

---

## generic agents

Below is a list of agents that you can directly use as they are generic. Also look for other agents in `agents` directory to use them as examples.

* [API Caller Agent](apicaller) - call any API
* [Form Agent](form) - present form to collect structured data
* [OpenAI Agent](openai) - call OpenAI 
