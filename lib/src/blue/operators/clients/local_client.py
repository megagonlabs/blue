###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs


###### Blue
from blue.operators.client import OperatorClient
from blue.tools.clients.local_client import LocalToolClient
from blue.utils import json_utils


###############
### LocalOperatorClient
#
class LocalOperatorClient(LocalToolClient, OperatorClient):
    def __init__(self, name, operators={}, properties={}):
        super().__init__(name, tools=operators, properties=properties)

    ######### operator
    def fetch_operators(self):
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        return self.fetch_tool_metadata(operator)

    ######### execute operator
    def execute_operator(self, operator, args, kwargs):
        return self.execute_tool(operator, args, kwargs)

    ######### refine operator
    def refine_operator(self, operator, args, kwargs):
        if operator is None:
            raise Exception("No operator matching...")

        result = []

        if operator in self.tools:
            operator_obj = self.tools[operator]
            result = operator_obj.refiner(**kwargs)

        return result
