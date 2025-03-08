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

---
# Text Processing Agents

---

Text processing is a fundamental step in the workflows of NLP applications. To facilitate this, two agents have been designed: `SemFilter` that filters documents based on a user-defined natural language expression, and  `SemExtract` that extracts values for pre-defined attributes from the documents.

## Text Processing Agents in Action

The following animation displays filtering and extraction over job posting data in Singapore. 

![sem_filter](/docs/images/sem_filter.gif)

![sem_extract](/docs/images/sem_extract.gif)

## Input & Output

### Input

- **Filter Condition:** A natural language expression to filter the document.
- **Context:** The document to filter. Can be plain text, json or in any semi-structured format.

### Output
The agent outputs a JSON object containing the following fields:

```json
{
  "filter_condition": bool
}
```

### Input

- **Columns to Extract:** A dictionary of attribute names optionally with their descriptions to be extracted. 
- **Context:** The document to extract information from. Can be plain text, json or in any semi-structured format.

### Output
The agent outputs a JSON object containing the attribute names as fields:

```json
{
"attribute A": "<Value A>"
"attribute B": "<Value B>"
}
```

---

## Base Properties

The agent uses a set of properties to control its behavior. Key properties include:

- **OpenAI API Configuration:**
  - `openai.api`: Specifies the API to use (e.g., "ChatCompletion").
  - `openai.model`: Model selection such as `"gpt-4o-mini"`.
  - `openai.max_tokens`: Limits the number of tokens (e.g., `300`).
 
- **Input/Output Settings:**
  - `output_path`: Can be set to stream or file
  - `input_json`, `input_context`, `input_context_field`, `input_field`: Define how input data is structured.
  - `input_template`: Uses a prompt that inclues any context, input document and filter/extraction specifications.
 
### Configuration (UI)

Users can also modify the `agent_properties` dictionary to suit your OpenAI API keys, input template and execution preferences from the UI. 

---

## Try it out

To try out the agent, first follow the quickstart guide to install the Blue platform. Here are some examples to try: 


| **Context** | **Filter Condition** | **Output** |
|--------------------------------|---------|---------|
| context: "Job Title: Child Care Centre Cook, Company: Company_881, Location: 308 Tanglin Road, 247974, Holland Road, Employment Type: Full Time, Position: Non-Executive, Salary: Undisclosed, Job Posting Date: 10 May 2019, Application Deadline: 09 Jun 2019, Description: We are seeking a dedicated and experienced Child Care Centre Cook to prepare nutritious meals for children. The role involves menu planning, food preparation, and ensuring food safety standards are met. Ideal candidates should have a passion for child care and cooking, with the ability to work in a team-oriented environment." | filter condition: "job involves both cooking and teaching skills." |```{"filter_condition": false}```|
| context: "Job Title: Child Care Centre Cook, Company: Company_881, Location: 308 Tanglin Road, 247974, Holland Road, Employment Type: Full Time, Position: Non-Executive, Salary: Undisclosed, Job Posting Date: 10 May 2019, Application Deadline: 09 Jun 2019, Description: We are seeking a dedicated and experienced Child Care Centre Cook to prepare nutritious meals for children. The role involves menu planning, food preparation, and ensuring food safety standards are met. Ideal candidates should have a passion for child care and cooking, with the ability to work in a team-oriented environment." | filter condition: "job involves both cooking skills." |```{"filter_condition": true}```|
| context: "Job Title: Child Care Teacher, Company: Company_1370, Location: TradeHub 21, 16 Boon Lay Way, 609965, Jurong, Employment Type: Full Time, Position: Executive, Salary: $2,000 - $2,400 Monthly, Job Posting Date: 28 May 2019, Application Deadline: 27 Jun 2019, Description: We are looking for a passionate Child Care Teacher to join our team. The role involves creating a safe, nurturing, and engaging environment for young children, planning and implementing age-appropriate activities, and supporting the development of social, cognitive, and emotional skills. Candidates should possess relevant qualifications and experience in early childhood education." | filter condition: "background in early childhood education is mandatory." |```{"filter_condition": true}```|
| context: "Job Title: Child Care Teacher, Company: Company_1370, Location: TradeHub 21, 16 Boon Lay Way, 609965, Jurong, Employment Type: Full Time, Position: Executive, Salary: $2,000 - $2,400 Monthly, Job Posting Date: 28 May 2019, Application Deadline: 27 Jun 2019, Description: We are looking for a passionate Child Care Teacher to join our team. The role involves creating a safe, nurturing, and engaging environment for young children, planning and implementing age-appropriate activities, and supporting the development of social, cognitive, and emotional skills. Candidates should possess relevant qualifications and experience in early childhood education." | filter condition: "background in early childhood education is optional." |```{"filter_condition": false}```|


| **Context** | **Extract Columns** | **Output** |
|--------------------------------|---------|---------|
| context: "Job Title: Child Care Centre Cook, Company: Company_881, Location: 308 Tanglin Road, 247974, Holland Road, Employment Type: Full Time, Position: Non-Executive, Salary: Undisclosed, Job Posting Date: 10 May 2019, Application Deadline: 09 Jun 2019, Description: We are seeking a dedicated and experienced Child Care Centre Cook to prepare nutritious meals for children. The role involves menu planning, food preparation, and ensuring food safety standards are met. Ideal candidates should have a passion for child care and cooking, with the ability to work in a team-oriented environment." | columns to extract: {"involves teaching": "boolean value to indicate if job requires teaching skills", "occupation category": "occupation sector such as education, child development, healthcare, technology", "skills": "list of skills expected", "certifications": "any certifications required for the job"} |```{"involves teaching":false,"occupation category":"child development","skills":["menu planning","food preparation","food safety","teamwork"],"certifications":[]}```|
| context: "Job Title: Child Care Teacher, Company: Company_1370, Location: TradeHub 21, 16 Boon Lay Way, 609965, Jurong, Employment Type: Full Time, Position: Executive, Salary: $2,000 - $2,400 Monthly, Job Posting Date: 28 May 2019, Application Deadline: 27 Jun 2019, Description: We are looking for a passionate Child Care Teacher to join our team. The role involves creating a safe, nurturing, and engaging environment for young children, planning and implementing age-appropriate activities, and supporting the development of social, cognitive, and emotional skills. Candidates should possess relevant qualifications and experience in early childhood education." | columns to extract: {"is full-time": "boolean value to indicate if job is full time", "salary": "range of annual salary"} |```{"is_full_time":true,"salary":"$24,000 - $28,800 Annual"```|

---
# OPENAI___CLASSIFIER

---

OPENAI___CLASSIFIER is a derivative of the OPENAI agent, and is essentially a prompt template. This agent is used by the Dialog Manager agent to classify the user’s intent into one of several pre-defined plans.

Being a derivative agent, this agent has no unique properties. Instead, all of its properties are the same as the above base agent, such as  openai.api, open.model, input_context, and so on. Any input passed to this agent’s DEFAULT processor is injected into the ${input} field of the input_template before the request is sent to the OpenAI API.

Below are the recommended property values for this agent:

```
{
	"input_field": "messages",
	"openai.model": "gpt-4o",
	"openai.api": "ChatCompletion",
	"output_path": "$.choices[0].message.content",
	"openai.max_tokens": 150,
	"openai.top_p": 1,
	"openai.service": "ws://blue_service_openai:8001",
	"schema": {},
	"openai.frequency_penalty": 0,
	"input_context_field": "content",
	"input_context": "$[0]",
	"input_template": "You are an expert in intent classification and information extraction. Please identify the intent of the below user text and classify it into one of the below specified possible intents. Respond only with JSON in the following format, nothing else. JSON response format: {\"intent\": \"investigate\"}. Make sure the intent is an exact string match with one of the specified intents. ${input}",
	"openai.presence_penalty": 0,
	"input_json": "[{\"role\": \"user\"}]"
}
```







