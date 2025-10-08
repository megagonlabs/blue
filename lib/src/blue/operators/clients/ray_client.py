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
    """Ray client for operators, inherits from RayToolClient and OperatorClient."""

    def __init__(self, name, operators={}, properties={}):
        """Initialize the RayOperatorClient.

        Parameters:
            name: Name of the ray operator client.
            operators: List of operators to be included as a dictionary of Operator objects. Defaults to {}.
            properties: Properties for the client. Defaults to {}.
        """
        super().__init__(name, tools=operators, properties=properties)

    ######### operator
    def fetch_operators(self):
        """Fetch available operators from ray client.

        Returns:
            List of available operators.
        """
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        """Fetch metadata for a specific operator from ray client.

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

        Parameters:
            operator: Name of the operator.
            args: Arguments for the operator.
            kwargs: Keyword arguments for the operator.

        Raises:
            Exception: No operator matching

        Returns:
            List of possible refinements as DataPipeline objects.
        """
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

    def get_operator_attributes(self, operator):
        """Get attributes of a specific operator.

        Parameters:
            operator: Name of the operator.

        Raises:
            Exception: No operator matching

        Returns:

        """
        if operator is None:
            raise Exception("No operator matching...")

        attributes = {}

        if operator in self.tools:
            operator_obj = self.tools[operator]
            attributes = operator_obj.get_attributes()

        return attributes
