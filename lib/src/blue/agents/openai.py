###### Parsers, Formats, Utils
import logging

###### Blue
from blue.agent import Agent
from blue.agents.requestor import RequestorAgent
from blue.utils import string_utils, json_utils
from blue.tools.registry import ToolRegistry

import json

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S"
)


#########################
### RequestorAgent.OpenAIAgent
#
class OpenAIAgent(RequestorAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)

        self.TOOL_SEPARATOR = "___"

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

    def _start(self):
        super()._start()

        # initialize registry
        self._init_registry()

    def _init_registry(self):
        # create instance of tool registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = ToolRegistry(id=self.properties['tool_registry.name'], prefix=prefix, properties=self.properties)

    def convert_tool_schema_to_openai_format(self, tool_schema, server_name):
        openai_schema = {"type": "function"}

        tool_name = tool_schema["name"]
        canonical_name = self._get_canonical(server_name, tool_name)
        openai_schema["function"] = {"name": canonical_name, "description": tool_schema["description"], "parameters": {"type": "object", "properties": {}, "required": []}}

        # iterate over all parameters
        for p, values in tool_schema['properties']['parameters'].items():
            openai_schema["function"]["parameters"]["properties"][p] = {"type": values["type"]}
            if "items" in values:
                openai_schema["function"]["parameters"]["properties"][p]["items"] = values["items"]
            if values["required"]:
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

        for server_name in selected_servers:
            if properties['tool_discovery']:

                if "tool_discovery_similarity_threshold" in properties and properties["tool_discovery_similarity_threshold"]:
                    similarity_threshold = self.properties["tool_discovery_similarity_threshold"]
                else:
                    similarity_threshold = 0.5

                matched_tools = []
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
                            matched_tools.append(t)
                        else:
                            break
                    if score > similarity_threshold:
                        break
                    else:
                        page = page + 1

            else:
                matched_tools = self.registry.get_server_tools(server_name)

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
                        tool_schemas.append(openai_schema)

        return tool_schemas

    def _get_canonical(self, server_name, tool_name):
        return server_name + self.TOOL_SEPARATOR + tool_name

    def _extract_canonical(self, canonical_name):
        cs = canonical_name.split(self.TOOL_SEPARATOR)
        if len(cs) >= 2:
            server_name = cs[0]
            tool_name = self.TOOL_SEPARATOR.join(cs[1:])
            return server_name, tool_name
        else:
            return cs[0], None

    def execute_api_call(self, input, properties=None, additional_data=None):
        if 'use_tools' in properties and properties['use_tools']:
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
                        args = json.loads(call["function"]["arguments"] or "{}")

                        # extract server and function from canonical
                        server_name, function_name = self._extract_canonical(canonical_name)
                        # execute tool
                        result = self.registry.execute_tool(function_name, server_name, None, args)
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
