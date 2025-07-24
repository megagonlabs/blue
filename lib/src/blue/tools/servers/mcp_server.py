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
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # server connection properties, host, protocol
        connection_properties = {}
        self.properties['connection'] = connection_properties
        connection_properties['protocol'] = "mcp"
        connection_properties['host'] = "0.0.0.0"
        connection_properties['port'] = 8123

    ##### connections
    def _connect(self, host="0.0.0.0", port=8123, protocol="mcp"):
        return FastMCP(name=self.name, json_response=False, stateless_http=False)

    def _start_connection(self):
        connection = self.properties['connection']
        self.connection = self._connect(**connection)

    def start(self):
        uvicorn.run(self.connection.streamable_http_app, host=self.properties['connection']['host'], port=self.properties['connection']['port'])

    ##### tools
    # override
    def initialize_tools(self):
        pass

    def add_tool(self, tool):
        self.connection.add_tool(tool.function, tool.name, tool.description)

    def list_tools(self):
        return asyncio.run(self.connection.list_tools())
