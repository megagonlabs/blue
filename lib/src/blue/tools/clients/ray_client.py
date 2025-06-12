###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import ray


###### Blue
from blue.tools.client import ToolClient
from blue.tools.tool import Tool
from blue.utils import json_utils

###### Ray Tools
from ray_tools import tools_dict


###############
### RayToolClient
#
class RayToolClient(ToolClient):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # server protocol 
        self.properties['protocol'] = "ray"

    ###### connection
    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        # init ray necessary
        host = c['host']
        port = c['port']
        server_url = "ray://" + host + ":" + str(port)
        ray.init(address=server_url)
        return {}

    def _disconnect(self):
        # TODO:
        return None

    ######### server
    def fetch_metadata(self):
        return {}

    ######### tool
    def fetch_tools(self):
        tools = ["add", "multiply"]
        return tools

    def fetch_tool_metadata(self, tool):
        metadata = {}

        if tool in tools_dict:
            tool_obj = tools_dict[tool]
            p = {}
            p = json_utils.merge_json(p, tool_obj.properties)
            p = json_utils.merge_json(p, { "parameters": tool_obj.parameters })
            metadata = {
                "name": tool_obj.name,
                "description": tool_obj.description,
                "properties": {
                    "parameters": p
                }
            }
        return metadata

   
    ######### execute tool
    def execute_tool(self, tool, args, kwargs):
        if tool is None:
            raise Exception("No tool matching...")

        result_ref = None

        if tool in tools_dict:
            tool_obj = tools_dict[tool]

            valid =  tool_obj.validator(kwargs)
            if valid:
                result_ref = tool_obj.function.remote(**kwargs)
            else:
                return valid

        if result_ref:
            result = ray.get(result_ref)
            return result
        else:
            return None

    
