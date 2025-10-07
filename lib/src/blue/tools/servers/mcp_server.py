###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs
import asyncio
from typing import Any
from contextlib import AsyncExitStack

import httpx
import uvicorn

from mcp.server.fastmcp import FastMCP

###### Blue
from blue.tools.server import ToolServer


#####
class MCPToolServer(ToolServer):
    """An MCPToolServer manages tools and handles MCP connections"""

    def __init__(self, name, properties={}):
        """Initialize an MCPToolServer instance.

        Parameters:
            name: Name of the tool server
            properties: Properties of the tool server
        """
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        """Initialize default properties for MCP tool server."""
        super()._initialize_properties()

        # server connection properties, host, protocol
        connection_properties = {}
        self.properties['connection'] = connection_properties
        connection_properties['protocol'] = "mcp"
        connection_properties['host'] = "0.0.0.0"
        connection_properties['port'] = 8123

    ##### connections
    def _connect(self, host="0.0.0.0", port=8123, protocol="mcp"):
        """Connect to MCP tool server.

        Parameters:
            host: Host address. Defaults to 0.0.0.0
            port: Port number. Defaults to 8123
            protocol: Protocol type. Defaults to "mcp"

        Returns:
            An MCP FastMCP server instance
        """
        return FastMCP(name=self.name, json_response=False, stateless_http=False)

    def _start_connection(self):
        """Start the MCP tool server connection."""
        connection = self.properties['connection']
        self.connection = self._connect(**connection)

    def start(self):
        """Start the MCP tool server."""
        uvicorn.run(self.connection.streamable_http_app, host=self.properties['connection']['host'], port=self.properties['connection']['port'])

    ##### tools
    # override
    def initialize_tools(self):
        """Initialize tools for MCP tool server. Override this method to add custom tools."""
        pass

    def add_tool(self, tool):
        """Add a tool to the MCP tool server.

        Parameters:
            tool: A Tool object
        """
        self.connection.add_tool(tool.function, tool.name, tool.description)

    def list_tools(self):
        """List available tools on the MCP tool server."""
        return asyncio.run(self.connection.list_tools())
