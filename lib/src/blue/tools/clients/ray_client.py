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


###############
### RayToolClient
#
class RayToolClient(ToolClient):
    def __init__(self, name, tools={}, properties={}):
        super().__init__(name, properties=properties)

        self.tools = tools

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

        namespace = None
        if 'namespace' in c:
            namespace = c['namespace']

        ray.init(address=server_url, namespace=namespace)
        return {}

    def _disconnect(self):
        # TODO:
        return None

    ######### server
    def fetch_metadata(self):
        return {}

    ######### tool
    def fetch_tools(self):
        return list(self.tools.keys())

    def fetch_tool_metadata(self, tool):
        metadata = {}

        if tool in self.tools:
            tool_obj = self.tools[tool]
            p = {}
            p = json_utils.merge_json(p, tool_obj.properties)
            p = json_utils.merge_json(p, {"signature": tool_obj.get_signature()})
            metadata = {"name": tool_obj.name, "description": tool_obj.description, "properties": p}
        return metadata

    ######### execute tool
    def execute_tool(self, tool, args, kwargs):
        if tool is None:
            raise Exception("No tool matching...")

        result_ref = None

        if tool in self.tools:
            tool_obj = self.tools[tool]

            valid = tool_obj.validator(kwargs)
            if valid:
                remote_function = ray.remote(tool.function)
                result_ref = remote_function.remote(**kwargs)
            else:
                return valid

        if result_ref:
            result = ray.get(result_ref)
            return result
        else:
            return None
