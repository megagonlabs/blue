###### Parsers, Formats, Utils
import logging
from typing import List, Dict, Any, Callable, Union, Optional, Any
from pydantic import BaseModel, ValidationError
import copy

###### Blue
from blue.utils import json_utils, tool_utils, log_utils
from blue.utils.type_utils import string_to_python_type, create_pydantic_model, validate_parameter_type


###############
### Tool
class Tool:
    """A tool is a function, it's signature, optionally properties, validator to validate input params, and explainer to describe output and potential errors"""

    def __init__(
        self, name: str, function: Callable[..., Any], description: str = None, properties: Dict[str, Any] = None, validator: Callable[..., Any] = None, explainer: Callable[..., Any] = None
    ):
        """Initialize a Tool instance.

        Parameters:
            name: Name of the tool
            function: The function that the tool will execute
            description: Description of the tool. Defaults to None.
            properties: Properties of the tool. Defaults to None.
            validator: A callable to validate input parameters. Defaults to None.
            explainer: A callable to explain the output. If None, no explanation is provided.
        """
        self.name = name
        if description is None:
            description = ""
        self.description = description
        self.properties = properties
        self.function = function
        self.validator = validator
        self.explainer = explainer

        # Initialize properties, parameters, validator, and explainer
        self._initialize(properties=properties)

    def _initialize(self, properties=None):
        """Initialize the tool with properties, logger, and signature.

        Parameters:
            properties: Properties to override default properties.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

        # signature
        self.properties['signature'] = {}
        self._extract_signature()

    def _initialize_properties(self):
        """Initialize default properties for tool."""
        self.properties = {}

        # Tool type
        self.properties["tool_type"] = "function"

    def get_properties(self, properties=None):
        """Get properties of the tool, with optional property overrides.

        Parameters:
            properties: Properties to override default properties.

        Returns:
            Merged properties dictionary.
        """
        if properties is None:
            properties = {}
        return json_utils.merge_json(self.properties, properties)

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )

    def _extract_signature(self):
        """Extract the signature of the tool's function and store it in properties."""
        signature = tool_utils.extract_signature(self.function, mcp_format=True)
        self.properties['signature'] = signature

    def get_signature(self):
        """Get the signature of the tool's function from properties.

        Returns:
            The signature of the tool's function as a dictionary.
        """
        return self.properties['signature']

    def get_parameters(self):
        """Get the parameters of the tool's function from its signature defined in properties.

        Returns:
            The parameters of the tool's function as a dictionary.
        """
        signature = self.get_signature()
        if signature:
            if 'parameters' in signature:
                return signature['parameters']
        return None

    def get_parameter(self, parameter):
        """Get a specific parameter's details from the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to retrieve.

        Returns:
            The details of the specified parameter as a dictionary, or None if not found.
        """
        parameters = self.get_parameters()
        if parameters:
            if parameter in parameters:
                return parameters[parameter]
        return None

    def get_parameter_type(self, parameter):
        """Get the type of a specific parameter from the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to retrieve.

        Returns:
            The type of the specified parameter, or None if not found.
        """
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'type' in parameter:
                return parameter['type']
        return None

    def set_parameter_description(self, parameter, description):
        """Set the description of a specific parameter in the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to set the description for.
            description: The description to set.

        Returns:
            The updated parameter details as a dictionary, or None if the parameter was not found.
        """
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['description'] = description
        return parameter

    def set_parameter_required(self, parameter, required):
        """Set whether a specific parameter is required in the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to set.
            required: Boolean indicating if the parameter is required.

        Returns:
            The updated parameter details as a dictionary, or None if the parameter was not found.
        """
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['required'] = required
        return parameter

    def set_parameter_hidden(self, parameter, hidden):
        """Set whether a specific parameter is hidden in the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to set.
            hidden: Boolean indicating if the parameter is hidden.

        Returns:

        """
        parameter = self.get_parameter(parameter)
        if parameter:
            parameter['hidden'] = hidden
        return parameter

    def is_parameter_required(self, parameter):
        """Check if a specific parameter is required in the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to check.

        Returns:

        """
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'required' in parameter:
                return parameter['required']
        return None

    def is_parameter_hidden(self, parameter):
        """Check if a specific parameter is hidden in the tool's function signature properties.

        Parameters:
            parameter: The name of the parameter to check.

        Returns:
            Boolean indicating if the parameter is hidden, or None if not found.
        """
        parameter = self.get_parameter(parameter)
        if parameter:
            if 'hidden' in parameter:
                return parameter['hidden']
        return None

    def get_returns(self):
        """Get the return of the tool's function from its signature defined in properties.

        Returns:
            The return of the tool's function as a dictionary.
        """
        signature = self.get_signature()
        if signature:
            if 'returns' in signature:
                return signature['returns']
        return None

    def get_returns_type(self):
        """Get the return type of the tool's function from its signature defined in properties.

        Returns:
            The return type of the tool's function, or None if not found.
        """
        returns = self.get_returns()
        if returns:
            if 'type' in returns:
                return returns['type']
        return None

    def set_returns_description(self, description):
        """Set the description of the return value in the tool's function signature properties.

        Parameters:
            description: The description to set.

        Returns:
            The updated return details as a dictionary, or None if the return was not found.
        """
        returns = self.get_returns()
        if returns:
            returns['description'] = description
        return returns
