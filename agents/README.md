# Agents

Below you will find more information on developing your own agents as well as a list of template and generic agents that you can use as a template and learn from.

Use below links for quick accces:
- [Agents](#agents)
  - [basics](#basics)
  - [data processor](#data-processor)
  - [messages](#messages)
  - [properties](#properties)
  - [tags](#tags)
  - [listeners](#listeners)
  - [memory](#memory)
  - [interactive agents](#interactive-agents)
  - [instructable agents](#instructable-agents)
  - [more details](#details)
- [Template Agents](#templates)
  - [template agent](#template-agent)
  - [template interactive agent](#template-interactive-agent)
- [Generic agents](#generic-agents)

</br>
</br>

---

## basics

Let's dive into a bit of development of the agents, starting with basics...

The `agents/lib` contains an Agent class that can be used as a base class for developing new agents. While it is often the practice to use Agent class as the base class, however, you do not necessarily need to extend the base class as you can simply use the Agent class directly, and pass in different parameters (such as `processor` function to process data).

Let's first go through an example that basically uses Agent class directly. You can find this example in `agents/test` directory. To setup for this example:

```
$ cd agents/test
$ pip install -r requirements.txt
$ ./build_agent.sh
```

Then, invoke a python interpreter (in `agents/test` directory):
```
$ python
```

First, to import Agent class, `import sys` so that you can access classes defined in various directories under `lib`. Afterwards, import `Agent` and `Session`:
```
import sys
import logging

sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')

from agent import Agent
from session import Session
```

Initially, let's turn off a lot of the logging, by settting logging level to `ERROR`:
```
logging.getLogger().setLevel(logging.ERROR)
```

In this example, let's first create a session, then have a USER agent, simply using the existing Agent class,  input some text using the `interact` function of the Agent class.
```
# create a session
session = Session()

# create a user agent
user_agent = Agent(name="USER", session=session)

# user initiates an interaction
user_agent.interact("hello world!", eos=False)
user_agent.interact("i am an agent")
```

In the above code, USER agent sends two interactions (messsages). In the first `interact` function `eos` is set to `False` so that the USER ouput stream doesn't contain and `EOS` (End Of Stream) message, yet.

Now, let's create a COUNTER agent, again using the base Agent class. The counter agent will listen to the streams in the same session as the USER agent. Then, we define a `processor` function to process stream data.

The signature of the `processor` function is `(message, input=None, properties=None, worker=None)`. `message` is the message received from the stream to process, `input` is the input parameter name, default is `DEFAULT`. `properties` is the agent properties, and finally `worker` is the specific worker instance. 

Let's write below code to create a COUNTER agent with a custom `processor` function as below:

```
stream_data = []

def processor(message, input=None, properties=None, worker=None):
    if message.isEOS():
        # print all data received from stream
        print("Stream Data:")
        print(stream_data)
        # compute length of the stream data
        l = len(stream_data)
        print(l)
        # output to stream
        return l 
    elif message.isData():
        # store data value
        data = message.getData()
        print(data)
        stream_data.append(data)
        return None

# create a counter agent in the same session
counter_agent = Agent(name="COUNTER", session=session, processor=processor)
```

And run it:
```
$ python test.py 
hello world!
i am an agent
Stream Data:
['hello world!', 'i am an agent']
2
```

As you can see from the output above, two DATA messages are received, followed by an `EOS` message (a CONTROL message). When the output stream is created it automatically injects a `BOS` (Begin Of Stream) message but for the purposes of this example, we are ignoring it. Once the `EOS` message is received, the `processor` functions computes the length of all the data in stream (accumulated in `stream_data` variable) and returns the result (and thereby outputing the result into a new stream)

</br>
</br>

## data processor 

As you have seen above, the `processor` function is called on each message in a stream to process and as such the `processor` function is the key to an agents behavior. 

The typical pattern of processing is as below:
```
if message.isBOS():
   # initialize
elif message.isData():
   # process data in message
elif message.isEOS():
   # aggregate, return result
   return result
```

Upon processing the messages from stream and performing agent-specific computation, the agent can output its result into a new output stream(s) for further processing by other agents. An agent can do so either by returning the result in `processor` function (as shown above). or by using the `worker` instance (passed on to the `processor` function as a parameter) to write to streams (e.g. worker.write_data(3)). 

`processor` can return data either as a singleton of type int, float, str, or dict. The message `content_type` is automatically set based on the `type` of the data returned, i.e. `INT`, `FLOAT`, `STR`, or `JSON`

`processor` can also return data in a list. In this case, each element in the list is written to the stream separately.

`worker` has a number of function that can be used to write to streams: `write_bos`, `write_eos`, `write_data`, `write_control`, and `write`. `write_bos` and `write_eos` functions are shorthand to output `BOS` and `EOS` control messages. `write_data` takes a data parameter and outputs a `DATA` message, e,g. `write_data(3), write_data("hello"), write_data({'a': 3})`. `write_control` take `code` and `args` parameters and outputs a `CONTROL` message. Finally, `write` function outputs any message. 

Each of these functions also take optional parameters: `output="DEFAULT", id=None, tags=None` where `output` is the output parameter name, `id` is an additional specific identifier on the output parameter, `tags` specify additional tags that can be set on the output stream.


Note messages in a stream can also be control messages. If an agent want to process such messages, they can do so, as shown below:
```
...
elif message.isControl():
   # process control message
...
```
See [messages](#messages) for further details on messages and more.

`input` is a parameter to the `processor` function. As agents can have multiple input parameters, if a stream is identified to be a particular input parameter, `input` parameter will be set to the name of the input parameter. See below [listeners](#listeners) to see how can identification is made. 

`properties` is another parameter to the `processor` function. It is essentially an agent's properties, which can be used in `processor` function to define the behavior of the computation. `properties` is essentially a dictionay object (can be nested) and specifici properties can be obtained simply by `properties[<property>]`, e.g. `properties["model"]`. See below [properties](#properties) for common and agent-specific properties.

</br>
</br>

## messages

In blue there are two types of messages: `DATA` and `CONTROL`. Messages have three parts: (1) `label`, either `DATA` of `CONTROL` (2) `contents`, serialized content of the message, and (3) `content_type`, either `INT`, `FLOAT`, `STR`, or `JSON`. 

For `DATA` messages its content is the data itself, for example, 3 or "Hello". For content of type `JSON`, `contents` is the string version of the JSON object.

For `CONTROL` messages its content is: (1) `code`, specific control code, (2) `args` JSON object containing arguments for the message. `content_type` of `CONTROL` messages is always `JSON`. Besides `BOS` and `EOS`, there are other control codes such as
`JOIN_SESSION` in platform streams `ADD_AGENT`, `REMOVE_AGENT`, `ADD_STREAM`, in session streams, and `EXECUTE_AGENT`, `CREATE_FORM`, `UPDATE_FORM`, and `CLOSE_FORM` in agent streams.

Message is a python class, that can be imported from `lib/platform/message`. It has a number of utility functions, to determine the type of message, such as `isData`, `isControl`, `isBOS`, `isEOS`, get parts of the message such as `getLabel`, `getData`, `getContents`, `getContentType`, `getCode`, `getArgs`, and `getArg`.

Additionally when a message is received from the `processor` function it additionally has an `id` and `stream`, capturing id of the message and the id of the stream it resides. These can be obtained through `getID` and `getStream` functions.

When returned from the `processor` function, message object itself can be used, for example:
```
return Message.EOS
return [3, Message.EOS]
```

</br>
</br>

## properties

Agents have a number of system specific properties as well as custom agent-specific properties. In the basic example, if you were to print the properties in the processor function, you would see:
```
{'db.host': 'localhost', 'db.port': 6379, 'instructable': True, 'listens': {'DEFAULT': {'includes': ['.*'], 'excludes': []}}, 'tags': {'DEFAULT': []}}
```

Above `db.host`, `db.port` would be system specific and set outside the context of agent, as part of the platform deployment. 
There are also generic properties such as `listens` and `tags` that are defined for each agent specifying which streams to listen to and how to tag output streams. See [listeners](#listeners) and [tags](#tags) for more details. `instructable` is another generic property, which states that this agent can be instructed to execute externally by another agent (such as planner). See  [instructable agents](#instructable-agents) for more details.

Beyond that any property is agent-specific and can be set to any key, value pair, and can be nested, as long as it can be serialized into JSON. Properties can be set hardcoded in code, set programmatically or interactively.


</br>
</br>

## tags

Each agent defines a `tags` property which defines what to tag each output stream. As such the `tags` property is organized by output parameter type and then for each output parameter it is a list of tags. Note the default output parameter is `DEFAULT`. 

For example:
```
"tags": {
    "DEFAULT": [ "A", "B" ],
    "RESULT": ["C"]
}
```

In the above example the `DEFAULT` output stream is tagged with `A` and `B` and `RESULT` output stream is tagged with `C`.

Note, as you might recall tags on output streams can also be specified as part of the `write` functions on the `worker`.

</br>
</br>

## listeners
So, you might ask how did the `COUNTER` agent listened to output from the `USER` agent. 

To decide which agents to listen to which streams, each agent defines a `listens` property and `includes` and `excludes` list. The default values are:
```
"listens": {
   "DEFAULT": {
      "includes" = [".*"]
      "excludes" = []
   }
}
```

Above specification essentially says every agent in the session listens to every stream from any other agents with no exclusions. Internally though an agent is prevented to listen to its own stream to avoid any loops.

To build more complex workflows though the `listens` property can be set more specifically per input parameter of the agent. As you recall `DEFAULT` is the default input parameter. So, in the above specification the `includes` list contains a list of regular expressions that are matched against stream tags. For example, above `.*` matches any sequence of characters, as such `includes` matches any tag. The `excludes` list similarly contains a list of regular expressions. In the above example though the list is empty, as such there are no exclusions.

The mechanism of listening is as follows, with more details:

Agents tag each stream they create, as you have seen above, `USER` agent tagged its output stream as `USER`. Agents by default tag each stream they produce by their own name. Additional, tags can be provided as a property (`tags`), or at the time of creating a new stream (see [data processor](#data0processor) worker.write function tag parameter).

Other agents in the session check if their `includes` and `excludes` list against the tags of the stream. `includes` and `excludes` lists are ordered lists of regular expressions that are evaluated on stream tags. To decide if a stream should be listened to, first the `includes` list is processed. If none of the regular expressions is matched, the stream with the tags is not listened to. If any of the regular expressions is a match, a further check is made in the `excludes` list. If none of the `excludes` regular expressions is matched, the stream is listened. If any one of `excludes` is matched the stream is not listened to. 

Default `includes` list is ['.*'], i.e. all agents are listened to, and the default `excludes` list is `[]`. Both include and exclude list can include an element that is itself a list, e.g. `["A","B",["C","D"]]` to support conjunctions. For example, previous example is `A or B or (C and D)`.

Once a match is found a worker is initiated to begin processing data on that stream, with the `input` set to the parameter for which a match is found.
</br>
</br>

## memory 

Let's revisit the example on this page. You might have noted that `stream_data` is a variable, collecting all the data from the streams. When writing `processor` functions you would rarely do that as you might run the risk of losing computation if the worker thread dies. A better approach is to use a distributed memory that a worker can write its private data and read from. 

There are three scopes of shared memory: (a) session (b) stream (c) agent.  Below are API functions for reading and writing in these respective scopes. To allow this you will use the worker instance that is passed on to the `processor` function, as a keyword parameter, i.e. 
```
def processor(message, input=None, properties=None, worker=None):
```

and use the following worker functions to write data:

For private agent-specific data, you can call the following functions on the keyword parameter `worker`, `set_data(key, value)`, `append_data(key, value)`, `get_data(key)`, and `get_data_len(key)`. For example, worker.set_data('a', 3), and worker.get_data('a'). The value can be any JSON value. 

To share data among agents processing data from the same stream, you can use `set_stream_data(key, value)`, `append_stream_data(key, value)`, `get_stream_data(key)`, and `get_stream_data_len(key)`.

To share data among all agents in the session, you can use `set_session_data(key, value)`, `append_session_data(key, value)`, `get_session_data(key)`, and `get_session_data_len(key)`.

</br>
</br>

## interactive agents
Building interactive agents, i.e. agents that present the user a graphical user interface, for example a form to fill out, is possible through a declarative UI specification. In blue we use [JSONForms](https://jsonforms.io/) to facilitate that. 

Essentially the agent in its responses sends back a form that describes the ui layout, data schema, and associated data.  The web interface renders it accordingly. Along with the form, and event stream is created, where the `processor` of the agent can start consuming event from the web interface. The interactive agent then can send more messages, new user interfaces, or other events that changes the UI, accordingly. 

To support interactive agent development in the web interface there is a Form Designer tool that allows you to design ui and data schemas in an interactive manner, along with the documentation. 

To return a UI, simply return a CONTROL message or write an output stream, for example:
`worker.write_control(ControlCode.CREATE_FORM, args, output="FORM")`

where the `args` is a JSON object with `uischema`, `schema` and optionnaly `data` sections. For example:
```
args = {
      "schema": {
          "type": "object",
          "properties": {"name": {"type": "string"}}
      },
      "uischema": {
          "type": "VerticalLayout",
          "elements": [
              {
                  "type": "Control",
                  "label": "Name",
                  "scope": "#/properties/name"
              },
              {
                  "type": "Button",
                  "label": "Done",
                  "props": {
                      "intent": "success",
                      "action": "DONE"
                  }
              }
          ]
      }
  }
```

Above specification would render:
![Stream](./docs/images/ui.png)


To process events from the web interface, as the user interacts, you can check the `stream` parameter of the `processor` function. Event messages come from a stream with `<prefix>:EVENT_MESSAGE:<form>`, where `<prefix>` is the output stream of the interactive agent, and `<form>` is the form id of the form events are received from. Typically, events as `DATA` with the contents describing the target widget and values, e.g.:
`{"name_id": "desired_location", "form_id": "90d46b5e", "value": "mountain view, ca", "timestamp": 1718124950421}`, where
`name_id` is the name of the widget, `form_id` is the id of the form, and `value` is the current value of the widget. The processor, then does whathever is necessary to handle the event, as this part is application logic dependent. The widget can be disabled by sending `("INTERACTION",{"type": "DONE", "form_id": <form_id>}, "json")`.

</br>
</br>

---
## instructable agents

</br>
</br>

---

## details
et's turn on more logging to examine what is happening, by settting logging level to `INFO`:
```
logging.getLogger().setLevel(logging.INFO)
```

and also additionally insert more prints to output:
```
...
    elif message.isData():
        # print(input)
        # print(properties)
        # print(message)
        # print(message.getID())
        # print(message.getStream())
        # store data value
        data = message.getData()
...
```

and re-run it, and examine the log created.
```
$ python test.py
```

There are a lot of logs created, let's pull out a few to explain what is going on:




If you examine the logs (see below), you will see that we create a new stream `USER:275e2d0b` with `BOS` (begin-of-stream) and then put two `DATA` messages into the stream corresponding to the input text, and ended the stream with `EOS` (end-of-stream).

```
INFO:root:Streamed into USER:275e2d0b message {'label': 'BOS'}
[...]
INFO:root:Streamed into USER:275e2d0b message {'label': 'DATA', 'data': 'hello', 'type': 'str'}
INFO:root:Streamed into USER:275e2d0b message {'label': 'DATA', 'data': 'world!', 'type': 'str'}
INFO:root:Streamed into USER:275e2d0b message {'label': 'EOS'}
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

</br>
</br>

# Template Agents

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

# Generic Agents

Below is a list of agents that you can directly use as they are generic. Also look for other agents in `agents` directory to use them as examples.

* [API Caller Agent](apicaller) - call any API
* [Form Agent](form) - present form to collect structured data
* [OpenAI Agent](openai) - call OpenAI 
