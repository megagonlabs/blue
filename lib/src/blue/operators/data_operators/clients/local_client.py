###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Blue
from blue.utils import json_utils

###### Local Operators
from blue.operators.data_operators.clients.local_operators import operators_dict, get_available_operators, get_operator, validate_operator_exists

###### Data Operator Client
from blue.operators.data_operators.client import DataOperatorClient

###############
### LocalDataOperatorClient
#
class LocalDataOperatorClient(DataOperatorClient):
    def __init__(self, name="LocalDataOperatorClient", properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # server protocol 
        self.properties['protocol'] = "local"

    ######### server
    def fetch_metadata(self):
        return {
            "name": self.name,
            "description": "Local data operators server",
            "protocol": "local",
            "operators_count": len(get_available_operators())
        }

    ######### operator
    def fetch_operators(self):
        return get_available_operators()

    def fetch_operator_metadata(self, operator):
        metadata = {}

        if validate_operator_exists(operator):
            operator_obj = get_operator(operator)
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
            return {
                "operator": None,
                "parameters": kwargs,
                "result": [],
                "error": "No operator specified",
                "explain": {"error": "No operator matching..."}
            }

        result = {
            "operator": operator_name,
            "parameters": kwargs,
            "result": [],
            "error": None,
            "explain": {}
        }

        if validate_operator_exists(operator_name):
            try:
                operator_obj = get_operator(operator_name)

                valid = operator_obj.validator(kwargs)
                if valid:
                    function_result = operator_obj.function(**kwargs)
                    
                    result["result"] = function_result
                    
                    explanation = operator_obj.explainer(function_result, kwargs)
                    result["explain"] = explanation
                    
                else:
                    result["error"] = "Parameter validation failed"
                    result["explain"] = {"error": "Invalid parameters provided"}
                    
            except Exception as e:
                result["error"] = str(e)
                result["explain"] = {"error": f"Execution failed: {str(e)}"}
        else:
            result["error"] = f"Unknown operator: {operator_name}"
            result["explain"] = {"error": f"No operator matching '{operator_name}'"}

        return result 