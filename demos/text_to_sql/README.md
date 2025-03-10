# text to sql
This demo illustrates a GPT-based agent running against a service (GPT Service). 

More specifically:
* Ability to customize a generic GPT-based agent
* Deploy a service

## Running the Demo

* Start the OpenAI service, using:
  ```
  $ cd services\openai
  $ ./deploy_service.sh --port_mapping 8001:8001 --service openai --image blue-service-openai:v0.9
  ```
  
* Create a duplicate of the OpenAI agent, and name it `OpenAISQLQuery`, with the following properties (note the service address `openai.service`):
```
{
    "image": "blue-agent-nl2sql:v0.9",
    "openai.api": "Completion",
    "openai.model": "gpt-3.5-turbo-instruct",
    "output_path": "$.choices[0].text",
    "input_field": "prompt",
    "input_template": "### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n### A query to {input}\nSELECT",
    "output_template": "SELECT {output}",
    "openai.temperature": 0,
    "openai.max_tokens": 150,
    "openai.top_p": 1,
    "openai.frequency_penalty": 0,
    "openai.presence_penalty": 0,
    "openai.stop": [
        "#",
        ";"
    ],
    "listens": {
        "includes": [
            "USER"
        ],
        "excludes": []
    },
    "tags": [
        "SQL"
    ],
    "openai.service": "ws://blue_service_openai:8001"
}
```
* Deploy OpenAI agent in the default registery, if it isn't already running, using the UI:
  * Browse to Agents / FORM_JOB
  * Actions / Deploy
* Create a new session in the UI
  * Sessions / New
  * Add `OpenAISQLQuery` agent
* Interact in the UI:
  * In the User text area, enter `What is the capital of US?` as input
    
### Build 

If not built already build `OpenAI` agent, using:

```
$ cd agents/{agent_name}
$ ./docker_build_agent.sh
$ ./docker_publish_agent.sh
```

### Agent Registry

Agent registry should contain:
```
{
    "image": "blue-agent-nl2sql:v0.9",
    "openai.api": "Completion",
    "openai.model": "gpt-3.5-turbo-instruct",
    "output_path": "$.choices[0].text",
    "input_field": "prompt",
    "input_template": "### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n### A query to {input}\nSELECT",
    "output_template": "SELECT {output}",
    "openai.temperature": 0,
    "openai.max_tokens": 150,
    "openai.top_p": 1,
    "openai.frequency_penalty": 0,
    "openai.presence_penalty": 0,
    "openai.stop": [
        "#",
        ";"
    ],
    "listens": {
        "includes": [
            "USER"
        ],
        "excludes": []
    },
    "tags": [
        "SQL"
    ],
    "openai.service": "ws://blue_service_openai:8001"
}
```
