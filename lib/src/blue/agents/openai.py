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
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

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

        self.properties['openai.service'] = "ws://localhost:8001"

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
        self.properties['service.prefix'] = 'openai'


class OpenAIToolCallingAgent(OpenAIAgent):

    def convert_tool_schemas_to_openai_format(self, tool_schemas):
        tools = []
        for t in tool_schemas:
            current_tool = {"type": "function"}
            current_tool["function"] = {
                "name": t.name,
                "description": t.description,
                "parameters": {
                    "type": "object",
                    "properties": t.inputSchema['properties'],
                    "required": t.inputSchema['required']
                }
            }
            tools.append(current_tool)

        return tools

    def handle_api_call(self, stream_data, properties=None):
        properties = self.get_properties(properties=properties)

        input_data = " ".join(stream_data)
        if not self.validate_input(input_data, properties=properties):
            return 

        prefix = 'PLATFORM:' + properties['tools']['registry_name']
        id = properties['tools']['registry_id']
        tool_registry = ToolRegistry(id=id, prefix=prefix, properties={"db.host":properties['tools']['db_host']})
        tool_server = tool_registry.connect_server(properties['tools']['server_name'])
        tool_schemas = self.convert_tool_schemas_to_openai_format(tool_server.list_tools())

        input_object = self.create_message(input_data, properties=properties)
        input_object["tools"] = tool_schemas

        num_calls = 0
        while True and num_calls < self.properties['tools']["max_calling_depth"]:
            r = self.call_service(json.dumps(input_object))
            response = json.loads(r)

            response_message = response['choices'][0]['message']
            if 'tool_calls' in response_message and response_message['tool_calls']:
                input_object["messages"].append({"role": "assistant", "content": None, "tool_calls": response_message['tool_calls']})
                for call in response_message['tool_calls']:
                    fn = call["function"]["name"]
                    args = json.loads(call["function"]["arguments"] or "{}")
                    result = tool_server.execute_tool(fn, None, args)

                    input_object["messages"].append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": call["function"]["name"],
                            "content": json.dumps({"result": result}),
                        }
                    )
            else:  
                input_object["messages"].append({"role": "assistant", "content": response_message["content"]})
                return response_message["content"]
            
            num_calls += 1