# Agents

## api
APIAgent is a generic Agent that is designed to be a base class for a variety of agents that essentially talk to an API. To support this it has a number of properties designed to construct a message to the API from input and other properties and parse response from the API to build the right output. Below are the properties to support this:

`input_json`: Initializes input if JSON is the input format. When set to None, input is just text. Otherwise JSON is constructed from the value of this property and input is plugged in to the right place in the input json using below properties. 

`input_context`: Defines where in the input json input is plugged in using JSONPath.

`input_context_field`: Defines the input field name where input is plugged in.

`input_field`: Defines the input field of the API call. Input is set as the value of this property, as constructued from above process for constructing input. 

`input_template`: Defines the template of the input using a template. When set to None it is assumed that input is passed on without an additionally formatting. Otherwise, `input_template` is expected to be of the following format: `.....{var1}....{input}....{var2}...` where `var1` and `var2` is substituted from the corresponding properties of the agent, and `input` is coming from the input stream. 

`output_path`: Define where in the API response to find the output using JSONPath. For example, `$.result` would point to the `result` property in the response JSON.

`output_template`: Defines the template of the output (in a similar fashion as in `input_template` using a template. When set to None it is assumed that output is returned without an additionally formatting. Otherwise, `output_template` is expected to be of the following format: `.....{var1}....{output}....{var2}...` where `var1` and `var2` is substituted from the corresponding properties of the agent, and `output` is coming from the response, extracted through `output_path`. 

### openai
OpenAI has a number of models available through APIs. OpenAI agent is basically a wrapper around models offered. The agent has a webservice component that works with the APIs. To create an OpenAI agent:
```
$ cd agents/openai
$ python src/openai_agent.py --session <session_id> --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages"}'
```
As you see above details of the model (e.g. `gpt-4`), api (e.g. `ChatCompletion`), etc. are provided as input to the agent. In addition to prepare input data for the API and to fetch response you need to provide additional properties such as `input_field`, `input_context`, `input_concext_field`, and `output_path`. `input_field` is the name of the field to where text data is provided to the API (e.g. `prompt` for `text_davinci_003`, `messages` for `gpt-4`). `output_path` is json_path to where the API returns the resulting text in the response (e.g. `$.choices[0].message`). Some of the API calls require more structured input such as `ChatCompletion`. The JSON structure is specified in `input_json`, and where to insert input text data is provided as json_path in `input_context` and the associated input field name is provided in `input_context_field`. Note that any properties with the prefix `openai.` will be passed on to OpenAI API, everything else is used by the agent itself for data processing.

For the OpenAI agent you would also need to start a webservice that will proxy to OpenAI APIs . To start the service :
```
$ cd agents/openai
$ docker compose up 
```

Finally, to setup openai authentication, edit `openai.env` and replace `<openai_api_key>` with your API Keys. 

### nl2sql
OpenAI has models (e.g. 'text-davinci-003') that can convert natural language statements to SQL queries, optionally given a schema. To bring NL2SQL agent, all you need to do is to pass in properties that will allow OpenAI to make the proper calls, with the right prompts, and input/output processing:
```
$ cd agents/openai
#  python src/openai_agent.py --properties  '{"openai.api":"Completion","openai.model":"text-davinci-003","output_path":"$.choices[0].text","input_field":"prompt","input_template":"### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n###{input}\nSELECT","openai.max_tokens":100,"openai.temperature":0,"openai.max_tokens":150,"openai.top_p":1.0,"openai.frequency_penalty":0.0,"openai.presence_penalty":0.0,"openai.stop":["#", ";"],"schema":"","output_template":"SELECT {output}"}' --session
```

As you can see above details of the model (e.g. `text-davinci-003`), api (e.g. `Completion`), etc. are provided as input to the agent. Beyond what is discussed above there are other properties that are needed to process input and ouput appropriately. For example, to set the prompt that also takes in a schema you can set `input_template` and provide additional attributes that can be set from properties. Above we initialize a prompt string that takes in `schema` and `input` as attributes. `input` is set by the agent, which is essentially input stream data, i.e. user query. `schema` is set in the agent properties (above just initialized to empty string). Siimilarly, `output_template` defines what to put back into the stream. Above a prefix (e.g. `SELECT `) is prepended to data coming from the model so the complete query can be obtained. 

As above to run the agent you will need to start the service.

### postgres 
Postgres Agent essentially scans a stream for any valid SQL statements and executes the query against its database. To bring up a Postgress agent, you need to provide properties such as host name, port, database, etc. For example:
```
$ cd agents/postgres
# python src/postgres_agent.py --properties  '{"postgres.user":"postgres", "postgres.password":"example", "postgres.database":"mydatabase", "postgres.host":"host.docker.internal"}' --session <SESSION>
```
Note that any properties with the prefix `postgres.` will be passed on to Postgress service, everything else is used by the agent itself for data processing and preparation.

For the Postgress agent you would also need to start a webservice to execute queries on Postgres . To start the service :
```
$ cd agents/postgres
$ docker compose up 
```

The postgress database itself is part of the blue platform, and it runs when you bring up the platform services (as noted above in infrastructure)

### neo4j 
NEO4J Agent essentially scans a stream for any neo4j/CYPHER query statements and executes the query against its database. To bring up a NEO4J agent, you need to provide properties such as host name, etc. For example:
```
$ cd agents/neo4j
# python src/neo4j_agent.py --properties  '{"neo4j.user":"neo4j", "neo4j.password":"neo4j", "neo4j.host":"bolt://host.docker.internal"}' --session <SESSION>
```
Note that any properties with the prefix `neo4j.` will be passed on to NEO4J service, everything else is used by the agent itself for data processing and preparation.

For the NEO4J agent you would also need to start a webservice to execute queries on Postgres . To start the service :
```
$ cd agents/neo4j
$ docker compose up 
```

The neo4j database itself is part of the blue platform, and it runs when you bring up the platform services (as noted above in infrastructure)

### observer 
Observer Agent essentially consumes every stream in a session and outputs the contents into a readable format that can be used for demo and debugging purposes. To bring up an Observer agent, all you need is to pass the session to observe. For example:
```
$ cd agents/observer
# python src/observer.py  --session <SESSION>
```

### recorder 
Recorder Agent essentially consumes every JSON stream in a session to find matches and writes them to session memory for every agents consumtion. `records` property is an array of records which consists of `variable`, `query`, and `single`, where the recorder agent executes JSONPATH query in `query` and assigns it to `variable` in the session. When a variable assignment is made it is announced in the recorder's stream.
```
$ cd agents/recorder
# python src/recorder.py --properties '{"records":[{"variale":<name>,"query":<jsonpath_query>},...]}' --session <SESSION>
```
