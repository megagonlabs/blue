###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
# import ray


###### Blue
from blue.tools.server import ToolServer



###############
### RayServer
#
class RayServer(ToolServer):
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

        # TODO
        # cpy.connect(**c)
        return None

    def _disconnect(self):
        # TODO:
        return None

    ######### server
    def fetch_metadata(self):
        return {}

    ######### tool
    def fetch_tools(self):
        tools = [{}]
        return tools

    def fetch_tool_metadata(self, tool):
        return {}

   
    ######### execute tool
    def execute_tool(self, params, tool=None):
        if tool is None:
            raise Exception("No tool provided")
        
        result = []

        return result

