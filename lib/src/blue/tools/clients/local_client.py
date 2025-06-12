###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs

###### Blue
from blue.tools.client import ToolClient
from blue.tools.tool import Tool
from blue.utils import json_utils

###### Local Tools
from local_tools import tools_dict



###############
### LocalToolClient
#
class LocalToolClient(ToolClient):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # server protocol 
        self.properties['protocol'] = "local"

    ###### connection
    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        # no connection necessary
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

        result = None

        if tool in tools_dict:
            tool_obj = tools_dict[tool]

            valid =  tool_obj.validator(kwargs)
            if valid:
                return tool_obj.function(**kwargs)
            else:
                return valid
       
        return result

    
