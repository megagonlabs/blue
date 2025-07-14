###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs

###### Blue
from blue.operators.client import OperatorClient
from blue.tools.clients.mcp_client import MCPToolClient
from blue.utils import json_utils


###############
### MCPOperatorClient
#
class MCPOperatorClient(MCPToolClient, OperatorClient):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ######### operator
    def fetch_operators(self):
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        return self.fetch_tool_metadata(operator)

    ######### execute operator
    def execute_operator(self, operator, args, kwargs):
        return self.execute_tool(operator, args, kwargs)
