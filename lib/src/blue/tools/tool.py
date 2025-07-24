###### Parsers, Formats, Utils
import logging
from typing import List, Dict, Any, Callable, Union, Optional, Any
from pydantic import BaseModel, ValidationError
import copy

###### Blue
from blue.tools.tool import Tool
from blue.utils import json_utils, tool_utils
from blue.utils.type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type


###############
### Operator
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

        self._extract_signature()

    def _initialize_properties(self):
        """Initialize default properties for tool."""
        self.properties = {}

        # Tool type
        self.properties["tool_type"] = "function"

    def _get_properties(self, properties=None):
        if properties is None:
            properties = {}
        return json_utils.merge_json(self.properties, properties)

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _extract_signature(self, mcp_format=True):
        self.signature = tool_utils.extract_signature(self.function, mcp_format=mcp_format)
