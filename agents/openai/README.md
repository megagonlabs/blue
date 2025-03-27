# openai agent
OpenAI has a number of models available through APIs. OpenAI agent is basically a wrapper around models offered. The agent has a webservice component that works with the APIs. To create an OpenAI agent:
```
$ cd agents/openai
$ python src/openai_agent.py --session <session_id> --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages"}'
```
As you see above details of the model (e.g. `gpt-4`), api (e.g. `ChatCompletion`), etc. are provided as input to the agent. In addition to prepare input data for the API and to fetch response you need to provide additional properties such as `input_field`, `input_context`, `input_concext_field`, and `output_path`. `input_field` is the name of the field to where text data is provided to the API (e.g. `prompt` for `text_davinci_003`, `messages` for `gpt-4`). `output_path` is json_path to where the API returns the resulting text in the response (e.g. `$.choices[0].message`). Some of the API calls require more structured input such as `ChatCompletion`. The JSON structure is specified in `input_json`, and where to insert input text data is provided as json_path in `input_context` and the associated input field name is provided in `input_context_field`. Note that any properties with the prefix `openai.` will be passed on to OpenAI API, everything else is used by the agent itself for data processing.

For the OpenAI agent you would also need to start a webservice that will proxy to OpenAI APIs. To deploy the service :
```
$ cd services/openai
$ ./deploy_service.sh --port_mapping 8001:8001 --service openai --image blue-service-openai 
```
Make sure the `openai.service` property of the agent is set to `ws://blue_service_openai:8001` given above deployment of the OpenAI service.

To build the service:

First, edit `openai.env` and replace `<openai_api_key>` with your API Keys. 

Then, build the service:
```
$ cd services/openai
$ ./docker_build_service.sh 
```
