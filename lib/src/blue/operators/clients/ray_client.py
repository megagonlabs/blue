###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import ray

###### Blue
from blue.operators.client import OperatorClient
from blue.tools.clients.ray_client import RayToolClient
from blue.utils import json_utils


###############
### RayOperatorClient
#
class RayOperatorClient(RayToolClient, OperatorClient):
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

        result_ref = None

        if operator in self.tools:
            operator_obj = self.tools[operator]

            remote_function = ray.remote(operator_obj.refiner)
            result_ref = remote_function.remote(**kwargs)

        if result_ref:
            result = ray.get(result_ref)
            return result
        else:
            return []
