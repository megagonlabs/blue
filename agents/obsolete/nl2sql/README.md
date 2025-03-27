# nl2sql agent

OpenAI has models (e.g. 'text-davinci-003') that can convert natural language statements to SQL queries, optionally given a schema. To bring NL2SQL agent, all you need to do is to pass in properties that will allow OpenAI to make the proper calls, with the right prompts, and input/output processing:
```
$ cd agents/openai
#  python src/openai_agent.py --properties  '{"openai.api":"Completion","openai.model":"text-davinci-003","output_path":"$.choices[0].text","input_field":"prompt","input_template":"### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n###{input}\nSELECT","openai.max_tokens":100,"openai.temperature":0,"openai.max_tokens":150,"openai.top_p":1.0,"openai.frequency_penalty":0.0,"openai.presence_penalty":0.0,"openai.stop":["#", ";"],"schema":"","output_template":"SELECT {output}"}' --session
```

As you can see above details of the model (e.g. `text-davinci-003`), api (e.g. `Completion`), etc. are provided as input to the agent. Beyond what is discussed above there are other properties that are needed to process input and ouput appropriately. For example, to set the prompt that also takes in a schema you can set `input_template` and provide additional attributes that can be set from properties. Above we initialize a prompt string that takes in `schema` and `input` as attributes. `input` is set by the agent, which is essentially input stream data, i.e. user query. `schema` is set in the agent properties (above just initialized to empty string). Siimilarly, `output_template` defines what to put back into the stream. Above a prefix (e.g. `SELECT `) is prepended to data coming from the model so the complete query can be obtained. 

As above to run the agent you will need to start the service.