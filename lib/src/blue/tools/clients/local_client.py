###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs

###### Blue
from blue.tools.client import ToolClient
from blue.tools.tool import Tool
from blue.utils import json_utils


###############
### LocalToolClient
#
class LocalToolClient(ToolClient):
    """A LocalToolClient connects to local tools and interfaces with them"""

    def __init__(self, name, tools={}, properties={}):
        """Initialize a LocalToolClient instance.

        Parameters:
            name: Name of the tool client
            tools: A dictionary of tool name to Tool object
            properties: Properties of the tool client
        """
        super().__init__(name, properties=properties)

        self.tools = tools

    ###### connection
    def _initialize_connection_properties(self):
        """Initialize default connection properties for local tool client."""
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['protocol'] = 'local'

    ###### connection
    def _connect(self, **connection):
        """Connect to local tools.

        Returns:
            An empty dictionary since no connection is necessary for local tools.
        """
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        # no connection necessary
        return {}

    def _disconnect(self):
        """Disconnect from local tools.

        Returns:
            None
        """
        # TODO:
        return None

    ######### server
    def fetch_metadata(self):
        """Fetch metadata for the local tool client.

        Returns:
            An empty dictionary since no metadata is necessary for local tools.
        """
        return {}

    ######### tool
    def fetch_tools(self):
        """Get a list of available tools on local client.

        Returns:
            List of tool names
        """
        tools = list(self.tools.keys())
        return tools

    def fetch_tool_metadata(self, tool):
        """Fetch metadata for a specific tool on local client.

        Parameters:
            tool: Name of the tool

        Returns:
            Metadata dictionary for the tool
        """
        metadata = {}

        if tool in self.tools:
            tool_obj = self.tools[tool]
            p = {}
            p = json_utils.merge_json(p, tool_obj.properties)
            p = json_utils.merge_json(p, {"signature": tool_obj.get_signature()})
            metadata = {"name": tool_obj.name, "description": tool_obj.description, "properties": p}
        return metadata

    ######### execute tool
    def execute_tool(self, tool, args, kwargs):
        """Execute a specific tool on local client.

        Parameters:
            tool: Name of the tool
            args: Arguments for the tool function
            kwargs: Keyword arguments for the tool function

        Raises:
            Exception: If no tool matches the given name

        Returns:
            Result of the tool function execution or validation result
        """
        if tool is None:
            raise Exception("No tool matching...")

        result = None

        if tool in self.tools:
            tool_obj = self.tools[tool]

            valid = tool_obj.validator(**kwargs)
            if valid:
                return tool_obj.function(**kwargs)
            else:
                return valid

        return result
