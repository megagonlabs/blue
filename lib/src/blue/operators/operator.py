###### Parsers, Formats, Utils
import logging
from typing import List, Dict, Any, Callable, Union, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
import copy

###### Blue
from blue.tools.tool import Tool
from blue.utils import json_utils, tool_utils
from blue.utils.type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type

###############
### Operator


def default_operator_function(input_data: List[List[Dict[str, Any]]], params: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Default function for operator. It should be overridden by each operator."""
    return []


def default_operator_validator(params: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Default validator for operator parameters."""
    try:
        return default_params_validator(params, properties)
    except Exception as e:
        # validation error
        return False


def default_params_validator(params: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate actual parameters (params) using the parameter definitions in properties."""
    # Need to get the parameters definition and validation error handling from properties
    if properties is None:
        properties = {}
    parameters_def = properties.get("parameters", {})
    validation_error_handling = properties.get("validation_error_handling", "fail")

    # Validate required parameters
    for param_name, param_def in parameters_def.items():
        # check if required parameter is present
        required = param_def.get("required", False)
        if required and param_name not in params:
            return False

        # validate parameter type
        if param_name in params:
            param_value = params[param_name]
            param_type = param_def.get("type")
            if param_type:
                try:
                    if not validate_parameter_type(param_value, param_type):
                        return False
                except Exception as e:
                    # System failure in validation - handle based on configuration
                    error_msg = f"Parameter validation system error for '{param_name}': {e}"
                    if validation_error_handling == "fail":
                        # raise validation error
                        logging.error(error_msg)
                        raise e
                    elif validation_error_handling == "log":
                        logging.error(error_msg)
                        return False
                    else:  # skip
                        # Continue with validation (treat as if validation passed)
                        logging.info(error_msg)
    return True


def default_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> Dict[str, Any]:
    """Default explainer for operator output."""
    total_input_records = sum(len(data) for data in input_data)
    output_count = len(output) if isinstance(output, list) else 1

    explanation = {
        "output": output,  # maybe not needed
        "num_input_data": len(input_data),
        "num_input_records": total_input_records,
        "num_input_records_per_data": [len(data) for data in input_data],
        "num_output_data": len(output),
        "num_output_records": output_count,
        "transformation_ratio": output_count / total_input_records if total_input_records > 0 else 0,
        "parameters": params,
    }
    return explanation


class Operator(Tool):
    """
    Data in operator scope refers to JSON array of records (list of dictionaries) in Blue.
    Operator is a specialized Tool to perform data operations in Blue.
    Input data for operators: always expects multiple Data as [data_1, data_2, ...] (list of lists of dictionaries)
    Output data for operators: same as input data, always returns a list of JSON array of records. If there is only one data returned, it will return a list with one element (data).
    """

    def __init__(
        self,
        name: str,
        description: str,
        properties: Dict[str, Any] = None,
        function: Callable = None,
        validator: Callable = None,
        explainer: Callable = None,
    ):
        super().__init__(name, description, function, properties=properties, validator=validator, explainer=explainer)

        if validator is None:
            self.validator = default_operator_validator
        if explainer is None:
            self.explainer = default_operator_explainer

    def _initialize_properties(self):
        super()._initialize_properties()

        # Tool type
        self.properties["tool_type"] = "operator"

        # Operator identification properties
        self.properties["validate_input"] = True
        self.properties["validate_output"] = True
        self.properties["validation_error_handling"] = "fail"  # fail, log, skip
        # Processing properties
        self.properties["max_records"] = None  # None means no limit
        self.properties["timeout"] = 300  # 5 minutes timeout

        # Error handling properties
        self.properties["error_handling"] = "skip"  # fail, log, skip
        self.properties["log_processing_stats"] = True

        # Parameter definitions
        self.properties["parameters"] = {}

        # Hyperparameter definitions
        self.properties["hyperparameters"] = {}

    def _extract_signature(self, mcp_format=True):
        super()._extract_signature(mcp_format=mcp_format)

        # expand params with parameter metadata, in function signature parameters
        if 'params' in self.signature['parameters']:
            params = self.signature['parameters']['params']
            params['properties'] = copy.deepcopy(self.properties["parameters"])
            for p in params['properties']:
                param = params['properties'][p]
                param['type'] = tool_utils.convert_type_string_to_mcp(param['type'])

    def _get_parameters(self):
        return self.properties["parameters"]

    def _update_parameters(self, parameters=None):
        if parameters is None:
            return
        # override
        for p in parameters:
            self.properties["parameters"][p] = parameters[p]

    def _get_hyperparameters(self):
        return self.properties["hyperparameters"]

    def _update_hyperparameters(self, hyperparameters=None):
        if hyperparameters is None:
            return
        # override
        for p in hyperparameters:
            self.properties["hyperparameters"][p] = hyperparameters[p]

    ######### Seperation functions to let LLM or other caller know if it's an operator or a function
    @classmethod
    def is_operator(cls, function_or_operator) -> bool:
        """Check if a tool/operator is actually an operator."""
        if hasattr(function_or_operator, 'properties'):
            return function_or_operator.properties.get("tool_type") == "operator"
        return False

    @classmethod
    def get_tool_type(cls, function_or_operator) -> str:
        """Get the type of a function/operator."""
        if cls.is_operator(function_or_operator):
            return "operator"
        return "function"

    ######### class-method-based operator execution flow as optional version besides function based operator design
    # def execute_operator(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any] = {}) -> Dict[str, Any]:
    #     """
    #     Main entry point for operator execution.
    #     This method orchestrates the complete execution flow and returns a structured result.
    #     Args:
    #         input_data: List of data sources, each containing JSON array of records
    #         params: Operator-specific parameter values (actual values, not definitions)
    #     Returns:
    #         Dictionary containing result, error, and explanation
    #     """
    #     try:
    #         # Validate input_data
    #         if self.properties.get("validate_input", True) and not self._validate_input_data(input_data):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "parameters": params or {},
    #                 "result": [],
    #                 "error": "Invalid input_data format",
    #                 "explain": {"error": "input_data must be a list of lists of dictionaries"},
    #             }

    #         # Validate parameters
    #         if not self.validator(params or {}):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "parameters": params or {},
    #                 "result": [],
    #                 "error": "Parameter validation failed",
    #                 "explain": {"error": "Invalid parameters provided"},
    #             }

    #         # Execute operator-specific logic
    #         result = self._execute_operator_logic(input_data, params or {})

    #         # Validate output data
    #         if self.properties.get("validate_output", True) and not self._validate_io_data(result):
    #             return {
    #                 "operator": self.name,
    #                 "input_data": input_data,
    #                 "parameters": params or {},
    #                 "result": result,
    #                 "error": "Invalid output data format",
    #                 "explain": {"error": "output_data must be a list of lists of dictionaries"},
    #             }

    #         # Generate explanation
    #         explanation = self.explainer(result, input_data, params or {})
    #         return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": result, "error": None, "explain": explanation}

    #     except Exception as e:
    #         error_handling = self.properties.get("error_handling", "skip")

    #         if error_handling == "fail":
    #             raise e
    #         elif error_handling == "log":
    #             logging.error(f"Error in {self.name}, skipping: {str(e)}")
    #             return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}
    #         else:  # skip
    #             logging.info(f"Error in {self.name}, skipping: {str(e)}")
    #             return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}

    # def _validate_io_data(self, input_data: List[List[Dict[str, Any]]]) -> bool:
    #     """Validate input/output data format. It should be a list of lists of dictionaries."""
    #     if not isinstance(input_data, list):
    #         return False
    #     for data in input_data:
    #         if not isinstance(data, list):
    #             return False
    #         for item in data:
    #             if not isinstance(item, dict):
    #                 return False
    #     return True

    # def _execute_operator_logic(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    #     """
    #     Execute the actual operator-specific logic.
    #     This method contains the core logic for each operator type.
    #     Operators should override this method with their specific implementation.
    #     Args:
    #         input_data: List of datas, each containing JSON array of records
    #         params: Operator-specific parameter values
    #     Returns:
    #         List of datas, each containing JSON array of records
    #     """
    #     # Default implementation: return the datas as they are
    #     # Subclasses MUST override this with their specific logic
    #     return input_data
