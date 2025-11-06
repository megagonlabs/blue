###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.agents.requestor import RequestorAgent
from blue.utils import uuid_utils, string_utils, json_utils
from blue.tools.registry import ToolRegistry
from blue.constant import Separator
from blue.stream import Message, ControlCode


#########################
### RequestorAgent.OpenAIAgent
#
class OpenAIAgent(RequestorAgent):
    """Agent to interact with OpenAI's API, supporting tool usage and function calling.
    
    Properties (in addition to RequestorAgent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `service_url`      | `str`                 | `ws://localhost:8001` | The URL of the OpenAI service. |
    | `openai.api`      | `str`                 | `ChatCompletion` | The OpenAI API to use (e.g., ChatCompletion, Completion). |
    | `openai.model`    | `str`                 | `gpt-4o` | The OpenAI model to use for generating responses. |
    | `input_json`     | `str`                | `[{"role": "user"}]` | JSON template for the input messages. |
    | `input_context`  | `str`                 | `$[0]` | JSONPath to extract context from the input JSON. |
    | `input_context_field` | `str`            | `content` | The field in the context JSON to extract. |
    | `input_field`    | `str`                 | `messages` | The field in the input JSON to populate with messages. |
    | `input_template` | `str`                 | `${input}` | Template for formatting the user input. |
    | `output_path`   | `str`                 | `$.choices[0].message.content` | JSONPath to extract the output from the OpenAI response. |
    | `openai.stream`  | `bool`                | `False` | Whether to use streaming responses from OpenAI. |
    | `openai.max_tokens` | `int`              | `300` | Maximum number of tokens for the OpenAI response. |
    | `use_tools`     | `bool`                | `False` | Whether to enable tool usage. |
    | `tool_discovery` | `bool`               | `False` | Whether to enable tool discovery based on user input. |
    | `tool_servers`  | `list of str`        | `[]` | List of tool server names to use. If empty, all servers are considered. |
    | `tools`         | `list of str`        | `[]` | List of tool names or canonical names to use. If empty, all tools are considered. |
    | `tool_discovery_similarity_threshold` | `float` | `0.5` | Similarity threshold for tool discovery (lower is more similar). |
    | `tool_max_calling_depth` | `int`          | `5` | Maximum depth for tool calling recursion. |

    Inputs:
    - DEFAULT: Text input to be sent to OpenAI.

    Outputs:
    - DEFAULT: Generated text output from OpenAI, tagged as `AI`.
    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        """Initialize default properties for the OpenAI agent."""
        super()._initialize_properties()

        self.properties['service_url'] = "ws://localhost:8001"

        self.properties['openai.api'] = 'ChatCompletion'
        self.properties['openai.model'] = "gpt-4o"
        self.properties['input_json'] = "[{\"role\": \"user\"}]"
        self.properties['input_context'] = "$[0]"
        self.properties['input_context_field'] = "content"
        self.properties['input_field'] = "messages"
        self.properties['input_template'] = "${input}"
        self.properties['output_path'] = '$.choices[0].message.content'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 300

        # prefix for service specific properties
        self.properties['service_prefix'] = 'openai'

        # tool calling related
        self.properties['use_tools'] = False
        self.properties['tool_discovery'] = False
        self.properties['tool_servers'] = []
        self.properties['tools'] = []
        self.properties['tool_discovery_similarity_threshold'] = 0.5
        self.properties['tool_max_calling_depth'] = 5

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the OpenAI agent."""
        self.add_input("DEFAULT", description="Text input that will be sent to OPENAI")

    def _initialize_outputs(self):
        """Initialize outputs for the OpenAI agent, tagging output as AI."""
        self.add_output("DEFAULT", description="Generated text output from OPENAI", tags=["AI"])

    def _start(self):
        """Start the OpenAI agent, initializing the tool registry."""
        super()._start()

        # initialize registry
        self._init_registry()

        self.explanation_worker = None
        self.explanations = {}

    def _init_registry(self):
        """Initialize the tool registry for the OpenAI agent."""
        # create instance of tool registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = ToolRegistry(id=self.properties['tool_registry.name'], prefix=prefix, properties=self.properties)

    def _validate_tool_schema(self, tool_schema):
        """Validate the structure of a tool schema. Returns True if valid, False otherwise.

        Parameters:
            tool_schema: The tool schema to validate.

        Returns:
            True if the schema is valid, False otherwise."""
        # checks
        if 'name' not in tool_schema:
            return False
        if 'properties' not in tool_schema:
            return False
        if 'signature' not in tool_schema['properties']:
            return False
        if 'parameters' not in tool_schema['properties']['signature']:
            return False
        return True

    def convert_tool_schema_to_openai_format(self, tool_schema, server_name):
        """Convert a tool schema to OpenAI's function calling format.

        Parameters:
            tool_schema: The tool schema to convert.
            server_name: The name of the server hosting the tool.

        Returns:
            The tool schema in OpenAI format, or None if the schema is invalid.
        """
        if not self._validate_tool_schema(tool_schema):
            return None

        openai_schema = {"type": "function"}

        tool_name = tool_schema["name"]
        canonical_name = self._get_canonical(server_name, tool_name)
        openai_schema["function"] = {"name": canonical_name, "description": tool_schema["description"], "parameters": {"type": "object", "properties": {}, "required": []}}

        # iterate over all parameters

        for p, values in tool_schema['properties']['signature']['parameters'].items():
            # skip hidden
            if 'hidden' in values and values['hidden']:
                continue

            t = 'unknown'
            if 'type' in values:
                t = values['type']
            openai_schema["function"]["parameters"]["properties"][p] = {"type": t}
            # copy over items
            if 'items' in values:
                openai_schema["function"]["parameters"]["properties"][p]["items"] = values["items"]
            # separately aggregate required parameters
            if 'required' in values and values["required"]:
                openai_schema["function"]["parameters"]["required"].append(p)

        return openai_schema

    def get_tool_schemas(self, user_input, properties):
        """Retrieve tool schemas based on user input and properties.

        Parameters:
            user_input: The user input to base tool selection on.
            properties: The properties dict containing tool selection criteria.

        Returns:
            A list of tool schemas in OpenAI format.
        """
        # intialize
        selected_servers = []
        selected_tools = []

        if 'tool_servers' in properties and properties['tool_servers']:
            selected_servers = properties['tool_servers']

        if 'tools' in properties and properties['tools']:
            selected_tools = properties['tools']

        tool_schemas = []

        if len(selected_servers) == 0:
            selected_servers = [server['name'] for server in self.registry.get_servers()]

        
        for server_name in selected_servers:
            matched_tools = []
            
            if properties['tool_discovery']:
                if "tool_discovery_similarity_threshold" in properties and properties["tool_discovery_similarity_threshold"]:
                    similarity_threshold = self.properties["tool_discovery_similarity_threshold"]
                else:
                    similarity_threshold = 0.5

                page = 0

                # progressively get more pages within similarity threshold
                while True:
                    results = self.registry.search_records(user_input, scope="/server/" + server_name, approximate=True, type="tool", page=page, page_size=5, page_limit=10)

                    if len(results) == 0:
                        break
                    for result in results:
                        score = float(result['score'])
                        if score < similarity_threshold:
                            t = self.registry.get_server_tool(server_name, result['name'])
                            if t:
                                matched_tools.append(t)
                        else:
                            break
                    if score > similarity_threshold:
                        break
                    else:
                        page = page + 1

            else:
                tools = self.registry.get_server_tools(server_name)
                if tools:
                    matched_tools.extend(tools)

            self.logger.info(matched_tools)
            if matched_tools:
                for t in matched_tools:
                    tool_name = t['name']
                    selected = False

                    # filter by selected tools, if there is one
                    if len(selected_tools) > 0:
                        if tool_name in selected_tools:
                            selected = True
                        if self._get_canonical(server_name, tool_name) in selected_tools:
                            selected = True
                    else:
                        selected = True

                    if selected:
                        openai_schema = self.convert_tool_schema_to_openai_format(t, server_name)
                        if openai_schema:
                            tool_schemas.append(openai_schema)

        return tool_schemas

    def _get_canonical(self, server_name, tool_name):
        """Get the canonical name for a tool given its server and tool names.

        Parameters:
            server_name: The name of the server hosting the tool.
            tool_name: The name of the tool.

        Returns:
            The canonical name for the tool.
        """
        return server_name + Separator.TOOL + tool_name

    def _extract_canonical(self, canonical_name):
        """Extract server and tool names from a canonical tool name.

        Parameters:
            canonical_name: The canonical name to extract from.

        Returns:
            A tuple containing the server name and tool name (or None if not present).
        """
        cs = canonical_name.split(Separator.TOOL)
        if len(cs) >= 2:
            server_name = cs[0]
            tool_name = Separator.TOOL.join(cs[1:])
            return server_name, tool_name
        else:
            return cs[0], None

    def write_tool_explanation(self, tool, arguments, result, eos=False):
        """Write an explanation of a tool call to the explanation output.

        Parameters:
            tool: The name of the tool called.
            arguments: The arguments passed to the tool.
            result: The result returned by the tool.
            eos: Whether to send an end-of-stream signal after the explanation. Defaults to False.
        """
        if self.explanation_worker is None:
            self.explanation_worker = self.create_worker(None)

        # cast to string
        tool = str(tool)
        arguments = json.dumps(arguments)
        result = str(result)

        explanation = []
        update = True
        if self.explanation_id in self.explanations:
            explanation = self.explanations[self.explanation_id]
        else:
            self.explanations[self.explanation_id] = explanation
            update = False

        tool_call = "<details>"
        tool_call += "<summary>" + "Tool: " + tool + "</summary>"
        tool_call += "Arguments: " + arguments + "\n"
        tool_call += "Result: " + result + "\n"
        tool_call += "</details>"

        explanation.append(tool_call)
        # form
        form_id = str(self.explanation_id)
        form = {
            "form_id": form_id,
            "schema": {},
            "uischema": {"type": "Markdown", "scope": "#/properties/markdown", "props": {"style": {}}},
            "data": {"markdown": "### Tool Calls\n" + "\n".join(explanation)},
        }
        # write markdown
        if update:
            self.explanation_worker.write_control(ControlCode.UPDATE_FORM, form, output="EXPLANATION", id=form_id)
        else:
            self.explanation_worker.write_control(ControlCode.CREATE_FORM, form, output="EXPLANATION", id=form_id)

    def execute_api_call(self, input, properties=None, additional_data=None):
        """Execute an API call to OpenAI, optionally using tools if specified in properties.

        Parameters:
            input: The input data for the API call.
            properties: Additional properties for the API call.
            additional_data: Any additional data to include in the API call.

        Returns:
            The output from the API call.
        """
        if 'use_tools' in properties and properties['use_tools']:

            # create a new id for each tool calling
            self.explanation_id = uuid_utils.create_uuid()

            # create message from input
            message = self.create_message(input, properties=properties, additional_data=additional_data)

            # inject tool data into message
            canonical_tool_schemas = self.get_tool_schemas(input, properties)
            message["tools"] = canonical_tool_schemas

            # initial num calls
            num_calls = 0

            # iteratively call until max depth
            while True and num_calls < properties["tool_max_calling_depth"]:
                # serialize message, call service
                url = self.get_service_address(properties=properties)
                m = json.dumps(message)
                r = self.call_service(url, m)

                response = json.loads(r)

                # check if response contains tool call, if so execute
                response_message = response['choices'][0]['message']
                if 'tool_calls' in response_message and response_message['tool_calls']:
                    message["messages"].append({"role": "assistant", "content": None, "tool_calls": response_message['tool_calls']})
                    for call in response_message['tool_calls']:
                        canonical_name = call["function"]["name"]
                        kwargs = json.loads(call["function"]["arguments"] or "{}")

                        # extract server and function from canonical
                        server_name, function_name = self._extract_canonical(canonical_name)
                        # execute tool
                        self.logger.info("Executing tool: " + function_name)
                        self.logger.info("Arguments: " + json.dumps(kwargs))

                        result = self.registry.execute_tool(function_name, server_name, None, kwargs)
                        self.logger.info("Result: " + str(result) + "\n")

                        self.write_tool_explanation(function_name, kwargs, result)

                        # append result to message
                        message["messages"].append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "name": canonical_name,
                                "content": json.dumps({"result": result}),
                            }
                        )
                else:

                    # create output from response
                    output = self.create_output(response, properties=properties)

                    # process output data
                    output = self.process_output(output, properties=properties)

                    return output

                # go on, until max depth
                num_calls += 1

        else:
            return super().execute_api_call(input, properties=properties, additional_data=additional_data)
