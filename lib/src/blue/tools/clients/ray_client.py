###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import ray


###### Blue
from blue.tools.client import ToolClient
from blue.tools.tool import Tool
from blue.utils import json_utils


###############
### RayToolClient
#
class RayToolClient(ToolClient):
    """A RayToolClient connects to a Ray ToolServer and interfaces with its tools"""

    def __init__(self, name, tools={}, properties={}):
        """Initialize a RayToolClient instance.

        Parameters:
            name: Name of the tool client
            tools: A dictionary of tool name to Tool object
            properties: Properties of the tool client
        """
        super().__init__(name, properties=properties)

        self.tools = tools

    ###### connection
    def _initialize_connection_properties(self):
        """Initialize default connection properties for Ray tool client."""
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 10001
        self.properties['connection']['protocol'] = 'ray'

    ###### connection
    def _connect(self, **connection):
        """Connect to Ray tool server."""
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        # init ray necessary
        host = c['host']
        port = c['port']
        server_url = "ray://" + host + ":" + str(port)

        namespace = None
        if 'namespace' in c:
            namespace = c['namespace']

        ray.init(address=server_url, namespace=namespace, ignore_reinit_error=True)
        return {}

    def _disconnect(self):
        """Disconnect from Ray tool server."""
        if ray.is_initialized():
            ray.shutdown()
        return None

    ######### server
    def fetch_metadata(self):
        """Fetch metadata for the Ray tool server.

        Returns:
            An empty dictionary since no metadata is necessary for Ray tool server.
        """
        return {}

    ######### tool
    def fetch_tools(self):
        """Get a list of available tools on Ray tool server.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def fetch_tool_metadata(self, tool):
        """Fetch metadata for a specific tool on Ray tool server.

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
        """Execute a specific tool on Ray tool server.

        Parameters:
            tool: Name of the tool
            args: Arguments for the tool function
            kwargs: Keyword arguments for the tool function

        Raises:
            Exception: If no tool matches the given name

        Returns:
            Result of the tool execution
        """
        if tool is None:
            raise Exception("No tool matching...")

        result_ref = None

        if tool in self.tools:
            tool_obj = self.tools[tool]

            valid = tool_obj.validator(**kwargs)
            if valid:
                remote_function = ray.remote(tool_obj.function)
                result_ref = remote_function.remote(**kwargs)
            else:
                return None

        if result_ref:
            result = ray.get(result_ref)
            return result
        else:
            return None
