###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Server specific libs

import argparse
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.types import TextContent
from mcp.client.streamable_http import streamablehttp_client

###### Blue
from blue.tools.client import ToolClient


###############
### MCPToolClient
#
class MCPToolClient(ToolClient):
    """An MCPToolClient connects to an MCP ToolServer and interfaces with its tools"""

    def __init__(self, name, properties={}):
        """Initialize an MCPToolClient instance.

        Parameters:
            name: Name of the tool client
            properties: Properties of the tool client
        """
        super().__init__(name, properties=properties)

    ###### connection
    def _initialize_connection_properties(self):
        """Initialize default connection properties for MCP tool client."""
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['protocol'] = 'mcp'
        self.properties['connection']['subprotocol'] = 'http'

    ###### connection
    def _connect(self, **connection):
        """Connect to MCP tool server."""
        self._init_connection(**connection)

    def _init_connection(self, **connection):
        """Initialize connection to MCP tool server.
        Parameters:
            connection: Connection parameters including host, port, protocol, subprotocol
        """
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        subprotocol = 'http'
        if 'subprotocol' in c:
            subprotocol = c['subprotocol']
            del c['subprotocol']

        # mcp server url
        host = c['host']
        port = c['port'] if 'port' in c else None

        self.server_url = subprotocol + "://" + host + (":" + str(port) if port else "") + "/mcp"

    async def _create_session(self):
        """Create an MCP client session asynchronously."""
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        self._streams_context = streamablehttp_client(
            url=self.server_url,
            headers={},
        )

        read_stream, write_stream, _ = await self._streams_context.__aenter__()

        self._session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()

    async def _release_session(self):
        """Release the MCP client session asynchronously."""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  # pylint: disable=W0125
            await self._streams_context.__aexit__(None, None, None)  # pylint: disable=E1101

    def _disconnect(self):
        """Disconnect from MCP tool server."""
        asyncio.run(self._release_session())

    ######### server
    def fetch_metadata(self):
        """Fetch metadata for the MCP tool server.

        Returns:
            An empty dictionary since no metadata is necessary for MCP tool server.
        """
        return {}

    ######### tool
    def fetch_tools(self):
        """Get a list of available tools on MCP tool server.

        Returns:
            List of tool names
        """
        return self.list_tools(detailed=False)

    def fetch_tool_metadata(self, tool):
        """Fetch metadata for a specific tool on MCP tool server.

        Parameters:
            tool: Name of the tool

        Returns:
            Metadata dictionary for the tool
        """
        result = self.list_tools(filter_tools=tool, detailed=True)
        if len(result) == 1:
            return result[0]
        else:
            return {}

    def list_tools(self, filter_tools=None, detailed=True):
        """List available tools on MCP tool server.

        Parameters:
            filter_tools: Tool name or list of tool names to filter. Defaults to None.
            detailed: Whether to return detailed tool information. Defaults to True.

        Returns:
            List of tools optionally with detailed tool information
        """
        return asyncio.run(self._list_tools(filter_tools=filter_tools, detailed=detailed))

    async def _list_tools(self, filter_tools=None, detailed=True):
        """List available tools on MCP tool server asynchronously.

        Parameters:
            filter_tools: Tool name or list of tool names to filter. Defaults to None.
            detailed: Whether to return detailed tool information. Defaults to True.

        Returns:
            List of tools optionally with detailed tool information
        """
        await self._create_session()

        tools = []
        try:
            response = await self.session.list_tools()
            for t in response.tools:
                if detailed:
                    tool = {}
                    tool['name'] = t.name
                    tool['description'] = t.description

                    properties = {}
                    tool['properties'] = properties

                    signature = {}
                    properties['signature'] = signature

                    parameters = {}
                    signature['parameters'] = parameters
                    returns = {'type': 'unknown'}
                    signature['returns'] = returns

                    # process tool schema
                    schema = t.inputSchema
                    required = []
                    if 'required' in t.inputSchema:
                        required = t.inputSchema['required']
                    schema_properties = t.inputSchema['properties']
                    for p in schema_properties:
                        schema_property = schema_properties[p]
                        parameter = {}
                        parameter['type'] = schema_property['type']
                        parameter['required'] = p in required
                        if 'items' in schema_property:
                            parameter['items'] = schema_property['items']
                        parameters[p] = parameter

                    if filter_tools:
                        if type(filter_tools) == str:
                            if t.name == filter_tools:
                                tools.append(tool)
                        elif type(filter_tools) == list:
                            if t.name in filter_tools:
                                tools.append(tool)
                    else:
                        tools.append(tool)
                else:
                    tools.append(t.name)
        finally:
            await self._release_session()
        return tools

    ######### execute tool
    def execute_tool(self, tool, args, kwargs):
        """Execute a specific tool on MCP tool server.

        Parameters:
            tool: Name of the tool
            args: Arguments for the tool function
            kwargs: Keyword arguments for the tool function

        Returns:
            Result of the tool execution
        """
        return asyncio.run(self._execute_tool(tool, args, kwargs))

    async def _execute_tool(self, tool, args, kwargs):
        """Execute a specific tool on MCP tool server asynchronously.

        Parameters:
            tool: Name of the tool
            args: Arguments for the tool function
            kwargs: Keyword arguments for the tool function

        Raises:
            Exception: If no tool is provided

        Returns:
            Result of the tool execution
        """
        if tool is None:
            raise Exception("No tool provided")

        await self._create_session()

        result = []
        try:
            response = await self.session.call_tool(tool, kwargs)
        finally:
            await self._release_session()

        if response:
            contents = response.content
            for content in contents:
                if type(content) == TextContent:
                    result.append(content.text)
        else:
            return []

        return result
