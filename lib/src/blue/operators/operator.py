###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging
from typing import List, Dict, Any, Callable, Union, Optional
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

###### Blue
from blue.tools.tool import Tool
from blue.utils import json_utils
from blue.utils.py_type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type

###############
### Operator


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
        """
        Initialize an Operator.
        Args:
            name: Name of the operator
            description: Description of what the operator does
            properties: properties for the operator, should include a key "parameters" with parameter definitions
            function: Function to execute the operator
            validator: Function to validate input parameters
            explainer: Function to explain output and potential errors
        """
        self.name = name
        self.description = description
        self.properties = properties
        self.validator = validator
        self.explainer = explainer

        # Initialize properties, parameters, validator, and explainer
        if properties is None:
            self.properties = {}
        if "parameters" not in self.properties:
            self.properties["parameters"] = {}
        if function is None:
            self.function = self._execute_operator_logic  # this is the function that each operator should override
        if validator is None:
            self.validator = self._default_validator
        if explainer is None:
            self.explainer = self._default_explainer

        self._initialize(properties=properties)

        super().__init__(name=name, description=description, properties=self.properties, function=self.execute_operator, parameters=parameters, validator=validator, explainer=explainer)

    def _initialize(self, properties=None):
        """Initialize the Operator following the same pattern as Agent."""
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        """Initialize default properties for operators."""
        self.properties = {}

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

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def get_properties(self, properties=None):
        if properties is None:
            properties = {}
        return json_utils.merge_json(self.properties, properties)

    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate actual parameters (params) using the parameter definitions in properties."""
        parameters = self.properties.get("parameters", {})
        validation_error_handling = self.properties.get("validation_error_handling", "fail")

        # Validate required parameters
        for param_name, param_def in parameters.items():
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

    def _default_validator(self, params: Dict[str, Any]) -> bool:
        """Default validator for operator parameters."""
        try:
            return self.validate_parameters(params)
        except Exception as e:
            # validation error
            return False

    def _default_explainer(self, output: Any, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> Dict[str, Any]:
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
            "properties": self.properties,  # maybe not needed
        }
        return explanation

    def execute_operator(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Main entry point for operator execution.
        This method orchestrates the complete execution flow and returns a structured result.
        Args:
            input_data: List of data sources, each containing JSON array of records
            params: Operator-specific parameter values (actual values, not definitions)
        Returns:
            Dictionary containing result, error, and explanation
        """
        try:
            # Validate input_data
            if self.properties.get("validate_input", True) and not self._validate_input_data(input_data):
                return {
                    "operator": self.name,
                    "input_data": input_data,
                    "parameters": params or {},
                    "result": [],
                    "error": "Invalid input_data format",
                    "explain": {"error": "input_data must be a list of lists of dictionaries"},
                }

            # Validate parameters
            if not self.validator(params or {}):
                return {
                    "operator": self.name,
                    "input_data": input_data,
                    "parameters": params or {},
                    "result": [],
                    "error": "Parameter validation failed",
                    "explain": {"error": "Invalid parameters provided"},
                }

            # Execute operator-specific logic
            result = self._execute_operator_logic(input_data, params or {})

            # Validate output data
            if self.properties.get("validate_output", True) and not self._validate_io_data(result):
                return {
                    "operator": self.name,
                    "input_data": input_data,
                    "parameters": params or {},
                    "result": result,
                    "error": "Invalid output data format",
                    "explain": {"error": "output_data must be a list of lists of dictionaries"},
                }

            # Generate explanation
            explanation = self.explainer(result, input_data, params or {})
            return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": result, "error": None, "explain": explanation}

        except Exception as e:
            error_handling = self.properties.get("error_handling", "skip")

            if error_handling == "fail":
                raise e
            elif error_handling == "log":
                logging.error(f"Error in {self.name}, skipping: {str(e)}")
                return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}
            else:  # skip
                logging.info(f"Error in {self.name}, skipping: {str(e)}")
                return {"operator": self.name, "input_data": input_data, "parameters": params or {}, "result": [], "error": str(e), "explain": {"error": f"Execution failed: {str(e)}"}}

    def _validate_io_data(self, input_data: List[List[Dict[str, Any]]]) -> bool:
        """Validate input/output data format. It should be a list of lists of dictionaries."""
        if not isinstance(input_data, list):
            return False
        for data in input_data:
            if not isinstance(data, list):
                return False
            for item in data:
                if not isinstance(item, dict):
                    return False
        return True

    def _execute_operator_logic(self, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """
        Execute the actual operator-specific logic.
        This method contains the core logic for each operator type.
        Operators should override this method with their specific implementation.
        Args:
            input_data: List of datas, each containing JSON array of records
            params: Operator-specific parameter values
        Returns:
            List of datas, each containing JSON array of records
        """
        # Default implementation: return the datas as they are
        # Subclasses MUST override this with their specific logic
        return input_data

    ######### Seperation functions to let LLM or other caller know if it's an operator or a tool
    @classmethod
    def is_operator(cls, tool_or_operator) -> bool:
        """Check if a tool/operator is actually an operator."""
        if hasattr(tool_or_operator, 'properties'):
            return tool_or_operator.properties.get("tool_type") == "operator"
        return False

    @classmethod
    def get_tool_type(cls, tool_or_operator) -> str:
        """Get the type of a tool/operator."""
        if cls.is_operator(tool_or_operator):
            return "operator"
        return "tool"
