###### Parsers, Formats, Utils
import logging
from typing import List, Dict, Any, Callable, Union, Optional, Any
from pydantic import BaseModel, ValidationError
import copy

###### Blue
from blue.utils import json_utils, tool_utils
from blue.utils.type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type


###############
### Tool
class Tool:
    """A tool is a function, it's signature, optionally properties, validator to validate input params, and explainer to describe output and potential errors"""

    def __init__(
        self, name: str, function: Callable[..., Any], description: str = None, properties: Dict[str, Any] = None, validator: Callable[..., Any] = None, explainer: Callable[..., Any] = None
    ):
        self.name = name
        if description is None:
            description = ""
        self.description = description
        self.properties = properties
        self.function = function
        self.validator = validator
        self.explainer = explainer

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

        self.function = function
        self.validator = validator
        self.explainer = explainer

        # Initialize properties, parameters, validator, and explainer
        if properties is None:
            properties = {}

        self._initialize(properties=properties)

    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

        self.properties['signature'] = {}
        self._extract_signature()

    def _initialize_properties(self):
        """Initialize default properties for tool."""
        self.properties = {}

        # Tool type
        self.properties["tool_type"] = "function"

    def get_properties(self, properties=None):
        if properties is None:
            properties = {}
        return json_utils.merge_json(self.properties, properties)

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _extract_signature(self):
        signature = tool_utils.extract_signature(self.function, mcp_format=True)
        self.properties['signature'] = signature

    def get_signature(self):
        return self.properties['signature']

    def get_parameters(self):
        signature = self.get_signature()
        if signature:
            if 'parameters' in signature:
                return signature['parameters']
        return None

    def get_parameter(self, parameter):
        parameters = self.get_parameters()
        if parameters:
            if parameter in parameters:
                return parameters[parameter]
        return None

    def get_parameter_type(self, parameter):
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'type' in parameter:
                return parameter['type']
        return None

    def set_parameter_description(self, parameter, description):
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['description'] = description
        return parameter

    def set_parameter_required(self, parameter, required):
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['required'] = required
        return parameter

    def set_parameter_hidden(self, parameter, hidden):
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['hidden'] = hidden
        return parameter

    def is_parameter_required(self, parameter):
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'required' in parameter:
                return parameter['required']
        return None

    def is_parameter_hidden(self, parameter):
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'hidden' in parameter:
                return parameter['hidden']
        return None

    def get_returns(self):
        signature = self.get_signature()
        if signature:
            if 'returns' in signature:
                return signature['returns']
        return None

    def get_returns_type(self):
        returns = self.get_returns()
        if returns:
            if 'type' in returns:
                return returns['type']
        return None

    def set_returns_description(self, description):
        returns = self.get_returns()
        if returns:
            returns['description'] = description
        return returns
