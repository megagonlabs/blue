###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import ray


###### Blue
from blue.tools.server import ToolServer
from blue.tools.tool import Tool
from blue.utils import json_utils

###############
### Remote Tools
#
### add
@ray.remote
def add(numbers=None):
    result = 0
    for number in numbers:
        result += number
    return result

add_tool = Tool(
    name = "add",
    description = "adds numbers and returns the addition as a result",
    properties = {},
    function = add,
    parameters = {
        "numbers": { "type": "list[Union[int, str]", "required": True}           
    },
    validator = lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer = lambda output, params:  { "output": output, "params": params}
)

### multiply
@ray.remote
def multiply(numbers=None):
    result = 1
    for number in numbers:
        result *= number
    return result

multiply_tool = Tool(
    name = "multiply",
    description = "multiplies numbers and returns the multiplication ion as a result",
    properties = {},
    function = multiply,
    parameters = {
        "numbers": { "type": "list[Union[int, str]", "required": True}           
    },
    validator = lambda params: 'numbers' in params and type(numbers) == list and all([type(number) in [int, float] for number in numbers]),
    explainer = lambda output, params: { "output": output, "params": params}
)



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

        # init ray necessary
        host = c['host']
        port = c['port']
        ray.init(address="ray://" + host + ":" + str(port))
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
        if tool == "add":
            p = {}
            p = json_utils.merge_json(p, add_tool.properties)
            p = json_utils.merge_json(p, { "parameters": add_tool.parameters })
            metadata = {
                "name": add_tool.name,
                "description": add_tool.description,
                "properties": {
                    "parameters": p
                }
            }
        elif tool == "multiply":
            p = {}
            p = json_utils.merge_json(p, multiply_tool.properties)
            p = json_utils.merge_json(p, { "parameters": multiply_tool.parameters })
            metadata = {
                "name": multiply_tool.name,
                "description": multiply_tool.description,
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

        if tool == add_tool.name:
            valid =  add_tool.validator(kwargs)
            if valid:
                result_ref = add_tool.function.remote(**kwargs)
            else:
                return valid
        elif tool == multiply_tool.name:
            valid =  multiply_tool.validator(kwargs)
            if valid:
                result_ref = multiply_tool.function.remote(**kwargs)
            else:
                return valid

        if result_ref:
            result = ray.get(result_ref)
            return result
        else:
            return None

    
