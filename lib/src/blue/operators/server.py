###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.operators.operator import Operator
from blue.tools.server import ToolServer
from blue.utils import log_utils


###############
### OperatorServer
#
class OperatorServer(ToolServer):
    """Base server for operators following the same pattern as ToolServer."""

    def __init__(self, name, properties={}):
        """Initialize the OperatorServer.

        Parameters:
            name: Name of the operator server.
            properties: Properties for the server. Defaults to {}.
        """
        self.name = name

        self._initialize(properties=properties)

        self._start()

    # opertors
    def initialize_operators(self):
        """Initialize operators. Override in subclasses."""
        pass

    # override
    def add_operator(self, operator):
        """Add an operator to the server. Override in subclasses."""
        pass

    # override
    def list_operators(self):
        """List available operators on the server. Override in subclasses."""
        return []
