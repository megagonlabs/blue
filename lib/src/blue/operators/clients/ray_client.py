###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import ray

###### Blue
from blue.operators.client import OperatorClient
from blue.utils import json_utils

###### Ray Operators
from blue.operators.clients.ray_operators import operators_dict

###############
### RayOperatorClient
#
class RayOperatorClient(OperatorClient):
    def __init__(self, name="RayOperatorClient", properties={}):
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
        return {
            "name": self.name,
            "description": "Ray data operators server",
            "protocol": "ray",
            "operators_count": len(operators_dict)
        }

    ######### operator
    def fetch_operators(self):
        return list(operators_dict.keys())

    def fetch_operator_metadata(self, operator):
        metadata = {}

        if operator in operators_dict:
            operator_obj = operators_dict[operator]
            p = {}
            p = json_utils.merge_json(p, operator_obj.properties)
            p = json_utils.merge_json(p, {"parameters": operator_obj.parameters})
            metadata = {
                "name": operator_obj.name,
                "description": operator_obj.description,
                "properties": {
                    "parameters": p
                }
            }
        return metadata

    ######### execute operator
    def execute_operator(self, operator_name, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        if operator_name is None:
            raise Exception("No operator specified")

        result_ref = None

        if operator_name in operators_dict:
            operator_obj = operators_dict[operator_name]

            valid = operator_obj.validator(kwargs)
            if valid:
                result_ref = operator_obj.function.remote(**kwargs)
            else:
                return {
                    "operator": operator_name,
                    "parameters": kwargs,
                    "result": [],
                    "error": "Parameter validation failed",
                    "explain": {"error": "Invalid parameters provided"}
                }

        if result_ref:
            try:
                result = ray.get(result_ref)
                explanation = operator_obj.explainer(result, kwargs)
                return {
                    "operator": operator_name,
                    "parameters": kwargs,
                    "result": result,
                    "error": None,
                    "explain": explanation
                }
            except Exception as e:
                return {
                    "operator": operator_name,
                    "parameters": kwargs,
                    "result": [],
                    "error": str(e),
                    "explain": {"error": f"Execution failed: {str(e)}"}
                }
        else:
            return {
                "operator": operator_name,
                "parameters": kwargs,
                "result": [],
                "error": f"Unknown operator: {operator_name}",
                "explain": {"error": f"No operator matching '{operator_name}'"}
            } 