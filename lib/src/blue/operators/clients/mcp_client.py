###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs

###### Blue
from blue.operators.client import OperatorClient
from blue.tools.clients.mcp_client import MCPToolClient
from blue.utils import json_utils


###############
### MCPOperatorClient
#
class MCPOperatorClient(MCPToolClient, OperatorClient):
    """MCP client for operators, inherits from MCPToolClient and OperatorClient."""

    def __init__(self, name, properties={}):
        """Initialize the MCPOperatorClient.

        Parameters:
            name: Name of the MCP operator client.
            properties: Properties for the client. Defaults to {}.
        """
        super().__init__(name, properties=properties)

    ######### operator
    def fetch_operators(self):
        """Fetch available operators from MCP client.

        Returns:
            List of available operators.
        """
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        """Fetch metadata for a specific operator from MCP client.

        Parameters:
            operator: Name of the operator.

        Returns:
            Dictionary containing operator metadata.
        """
        return self.fetch_tool_metadata(operator)

    ######### execute operator
    def execute_operator(self, operator, args, kwargs):
        """Execute a specific operator with given arguments.

        Parameters:
            operator: Name of the operator.
            args: Arguments for the operator.
            kwargs: Keyword arguments for the operator.

        Returns:
            Result of the operator execution
        """
        return self.execute_tool(operator, args, kwargs)

    ######### refine operator
    def refine_operator(self, operator, args, kwargs):
        """Refine the operator based on given arguments, returns list of possible refinements as DataPipeline objects.
        Currently, MCP does not support operator refinement, so this method returns an empty list.

        Parameters:
            operator: Name of the operator.
            args: Arguments for the operator.
            kwargs: Keyword arguments for the operator.

        Returns:
            List of possible refinements as DataPipeline objects.
        """
        result = []
        return result

    def get_operator_attributes(self, operator):
        """Get attributes of a specific operator.
        Currently, MCP does not support fetching operator attributes, so this method returns an empty dictionary.

        Parameters:
            operator: Name of the operator.

        Returns:
            Dictionary of operator attributes.
        """
        attributes = {}
        return attributes
