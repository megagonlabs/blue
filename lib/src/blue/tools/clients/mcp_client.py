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
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # server protocol 
        self.properties['protocol'] = "mcp"

    ###### connection
    def _connect(self, **connection):
        self._init_connection(**connection)

    def _init_connection(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        # mcp server url
        host = c['host']
        port = c['port']
        self.server_url = "http://" + host + ":" + str(port) + "/mcp" 

    async def _create_session(self):
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
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  # pylint: disable=W0125
            await self._streams_context.__aexit__(None, None, None)

    def _disconnect(self):
        asyncio.run(self._release_session())

    ######### server
    def fetch_metadata(self):
        return {}

    ######### tool
    def fetch_tools(self):
        return self.list_tools(detailed=False)

    def fetch_tool_metadata(self, tool):
        result = self.list_tools(filter_tools=tool, detailed=True)
        if len(result) == 1:
            return result[0]
        else:
            return {}

    def list_tools(self, filter_tools=None, detailed=True):
        return asyncio.run(self._list_tools(filter_tools=filter_tools, detailed=detailed))

    async def _list_tools(self, filter_tools=None, detailed=True):
        await self._create_session()

        tools = []
        try:
            response = await self.session.list_tools()
            tools = response.tools
        finally:
            await self._release_session()
        return tools

    ######### execute tool
    def execute_tool(self, tool, args, kwargs):
        return asyncio.run(self._execute_tool(tool, args, kwargs))

    async def _execute_tool(self, tool, args, kwargs):
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

