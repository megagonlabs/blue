###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging
from typing import List, Dict, Any

###### Blue
from blue.tools.client import ToolClient


###############
### OperatorClient


class OperatorClient(ToolClient):
    """
    Base client for operators following the same pattern as ToolClient.
    Handles validation, execution, and result formatting for operators.
    """

    def __init__(self, name: str = "OperatorClient", properties: Dict[str, Any] = None):
        """Initialize the OperatorClient.

        Parameters:
            name: Name of the client. Defaults to "OperatorClient".
            properties: Properties for the client. Defaults to None.
        """
        super().__init__(name, properties=properties or {})

    ## _intialize, _start, _stop, _connect, _disconnect, _start_connection, _stop_connection, _initialize_properties, _update_properties inherited from ToolClient

    ######### server
    def fetch_metadata(self):
        """Fetch metadata about the operator client.

        Returns:
            Dictionary containing metadata information.
        """
        return self.fetch_metadata()

    ######### operator
    def fetch_operators(self):
        """Fetch available operators.

        Returns:
            List of available operators.
        """
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        """Fetch metadata for a specific operator.

        Parameters:
            operator: Name of the operator.

        Returns:
            Dictionary containing operator metadata.
        """
        return self.fetch_tool_metadata(operator)

    def execute_operator(self, operator, args=None, kwargs=None):
        """Execute a specific operator with given arguments.

        Parameters:
            operator: Name of the operator.
            args: Arguments for the operator. Defaults to None.
            kwargs: Keyword arguments for the operator. Defaults to None.

        Returns:
            Result of the operator execution
        """
        return self.execute_tool(operator, args=args, kwargs=kwargs)

    def refine_operator(self, operator, args=None, kwargs=None):
        """Refine the operator based on given arguments, returns list of possible refinements as DataPipeline objects.

        Parameters:
            operator: Name of the operator.
            args: Arguments for the operator. Defaults to None.
            kwargs: Keyword arguments for the operator. Defaults to None.

        Returns:
            List of possible refinements as DataPipeline objects.
        """
        return []

    def get_operator_attributes(self, operator):
        """Get attributes of a specific operator.

        Parameters:
            operator: Name of the operator.

        Returns:
            Dictionary of operator attributes.
        """
        return {}
