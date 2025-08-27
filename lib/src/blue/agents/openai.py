###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.agents.requestor import RequestorAgent
from blue.utils import uuid_utils, string_utils, json_utils
from blue.tools.registry import ToolRegistry
from blue.constant import Separator


#########################
### RequestorAgent.OpenAIAgent
#
class OpenAIAgent(RequestorAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)

    def _initialize_properties(self):
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
        self.add_input("DEFAULT", description="Text input that will be sent to OPENAI")

    def _initialize_outputs(self):
        self.add_output("DEFAULT", description="Generated text output from OPENAI", tags=["AI"])

    def _start(self):
        super()._start()

        # initialize registry
        self._init_registry()

        self.explanation_worker = None

    def _init_registry(self):
        # create instance of tool registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = ToolRegistry(id=self.properties['tool_registry.name'], prefix=prefix, properties=self.properties)

    def _validate_tool_schema(self, tool_schema):
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

        matched_tools = []
        for server_name in selected_servers:
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
        return server_name + Separator.TOOL + tool_name

    def _extract_canonical(self, canonical_name):
        cs = canonical_name.split(Separator.TOOL)
        if len(cs) >= 2:
            server_name = cs[0]
            tool_name = Separator.TOOL.join(cs[1:])
            return server_name, tool_name
        else:
            return cs[0], None

    def write_explanation(self, explanation, eos=False):
        if self.explanation_worker is None:
            self.explanation_worker = self.create_worker(None)
            self.explanation_id = uuid_utils.create_uuid()

        self.explanation_worker.write_data(explanation, output="EXPLANATION", id=self.explanation_id, tags=['EXPLANATION'], scope="worker")
        if eos:
            self.explanation_worker.write_eos(output="EXPLANATION", id=id, scope="worker")

    def execute_api_call(self, input, properties=None, additional_data=None):
        if 'use_tools' in properties and properties['use_tools']:

            # Explain tool use
            self.write_explanation("Using tools...\n")

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
                        self.write_explanation("Executing tool: " + function_name + "\n")

                        self.logger.info("Arguments: " + json.dumps(kwargs))
                        self.write_explanation("Arguments: " + json.dumps(kwargs) + "\n")
                        result = self.registry.execute_tool(function_name, server_name, None, kwargs)
                        self.logger.info("Result: " + str(result) + "\n")
                        self.write_explanation("Result: " + str(result) + "\n")
                        self.write_explanation("------------")
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
                    self.write_explanation("Done.", eos=True)

                    # create output from response
                    output = self.create_output(response, properties=properties)

                    # process output data
                    output = self.process_output(output, properties=properties)

                    return output

                # go on, until max depth
                num_calls += 1

        else:
            return super().execute_api_call(input, properties=properties, additional_data=additional_data)
