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


class OpenAIToolCallingAgent(OpenAIAgent):
    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['platform.name'] = "jackson" 
        self.properties['tool_sources'] = ["calculator_mcp"]
        self.properties['tool_max_calling_depth'] = 5
        self.properties['tool_discovery'] = False
        self.properties['tool_discovery_similarity_threshold'] = 1
        self.properties['tools'] = None

    def convert_tool_schemas_to_openai_format(self, tool_schemas):
        tools = []
        for t in tool_schemas:
            current_tool = {"type": "function"}
            current_tool["function"] = {
                "name": t["name"],
                "description": t["description"],
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            for p, values in t['properties']['parameters'].items():
                current_tool["function"]["parameters"]["properties"][p] = {
                    "type": values["type"]
                }
                if "items" in values:
                    current_tool["function"]["parameters"]["properties"][p]["items"] = values["items"]
                if values["required"]:
                    current_tool["function"]["parameters"]["required"].append(p)
            tools.append(current_tool)
        return tools
    
    def get_tool_schemas(self, tool_registry, user_input, properties):
        tool_schemas = []
        tools_to_server = {}
        
        if properties['tool_discovery']:
            logging.info("Tool Discovery WIP, passing")

            # search_results = tool_registry.search_records(user_input, approximate=True)
            # logging.info("Search results no scope")
            # logging.info(search_results)

            # if 'tool_sources' in properties and properties['tool_sources']:
            #     servers = properties['tool_sources']
            # else:
            #     servers = [s['name'] for s in tool_registry.get_servers()]
            # for server_name in servers:
            #     search_results = tool_registry.search_records(user_input, scope="/"+server_name, approximate=True)
            #     logging.info("Search results, with scope")
            #     logging.info(search_results)

            #     tool_registry.sync_server(server_name)
            #     search_results = tool_registry.search_records(user_input, scope="/"+server_name, approximate=True)
            #     logging.info("Search results, with scope, with sync")
            #     logging.info(search_results)

            #     tool_registry.sync_server(server_name)
            #     search_results = tool_registry.search_records(user_input, scope="/"+server_name, approximate=True, type="tool")
            #     logging.info("Search results, with scope, with sync, with type")
            #     logging.info(search_results)

            # if 'tool_sources' in properties and properties['tool_sources']:
            #     servers = properties['tool_sources']
            # else:
            #     servers = tool_registry.get_servers()

            # search_results = tool_registry.search_records(user_input, approximate=True)
            # if 'tool_sources' in properties and properties['tool_sources']:
            #     search_results = [s for s in search_results if s['name'] in properties['tool_sources']]
            
            # tool_sources = []
            # for s in search_results:
            #     if 'tool_sources' in properties and properties['tool_sources']:
            #         if s['name'] in properties['tool_sources']:
            #             tool_sources.append(s['name'])
            #     else:
            #         if ('tool_discovery_similarity_threshold' in properties and )


        else:
            for server_name in properties['tool_sources']:
                tool_registry.sync_server(server_name)
                tool_server_tools = tool_registry.get_server_tools(server_name)

                for t in tool_server_tools:
                    if t["name"] in tools_to_server:
                        logging.info(f"Duplicate tool {t["name"]} found in server {server_name}, disregarding.")
                    else:
                        tool_schemas.append(t)
                        tools_to_server[t["name"]] = server_name

        tool_schemas = self.convert_tool_schemas_to_openai_format(tool_schemas)
        if 'tools' in properties and properties['tools'] and tool_schemas:
            tool_schemas = [t for t in tool_schemas if t['function']['name'] in properties['tools']]

        return tool_schemas, tools_to_server

    def execute_api_call(self, stream_data, properties=None, additional_data=None):
        if properties is None:
            properties = self.get_properties(properties=properties)
        input_data = " ".join(stream_data)
        if not self.validate_input(input_data, properties=properties):
            return 

        platform_id = properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        tool_registry = ToolRegistry(id=properties['tool_registry.name'], prefix=prefix, properties=properties)
        tool_schemas, tools_to_server = self.get_tool_schemas(tool_registry, input_data, properties)        

        session_data = self.session.get_all_data()
        input_object = self.create_message(input_data, properties=properties, additional_data=session_data)
        input_object["tools"] = tool_schemas

        logging.info("Is service still in input?============================")
        logging.info("service" in input_object)

        input_object.pop("service")


        num_calls = 0
        while True and num_calls < properties["tool_max_calling_depth"]:
            logging.info("Input object")
            logging.info(input_object)
            url = self.get_service_address(properties=properties)
            r = self.call_service(url, json.dumps(input_object))
            response = json.loads(r)

            response_message = response['choices'][0]['message']
            if 'tool_calls' in response_message and response_message['tool_calls']:
                input_object["messages"].append({"role": "assistant", "content": None, "tool_calls": response_message['tool_calls']})
                for call in response_message['tool_calls']:
                    fn = call["function"]["name"]
                    args = json.loads(call["function"]["arguments"] or "{}")

                    result = tool_registry.execute_tool(fn, tools_to_server[fn], None, args)

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