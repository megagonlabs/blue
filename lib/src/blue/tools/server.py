###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.tools.tool import Tool
from blue.utils import log_utils


###############
### ToolServer
#
class ToolServer:
    """A ToolServer manages tools and handles connections"""

    def __init__(self, name, properties={}):
        """Initialize a ToolServer instance.

        Parameters:
            name: Name of the tool server
            properties: Properties of the tool server
        """
        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """Initialize the tool server with properties and logger.

        Parameters:
            properties: Properties to override default properties.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default properties for tool server."""
        self.properties = {}

        # server protocol
        self.properties['protocol'] = "default"

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """Initialize logger for the tool server."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("tool_server", self.name, -1)

    ###### connection
    def _start_connection(self):
        """Starts a connection to the tool server."""
        connection = self.properties['connection']

        self.connection = self._connect(**connection)

    def _stop_connection(self):
        """Stops the connection to the tool server."""
        self._disconnect()

    def _connect(self, **connection):
        """Connect to the tool server.

        Returns:
            A connection object or None
        """
        return None

    def _disconnect(self):
        """Disconnect from the tool server."""
        return None

    def _start(self):
        """Start the tool server, connect, and initialize tools."""
        # self.logger.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize tools
        self.initialize_tools()

        self.logger.info('Started server {name}'.format(name=self.name))

    def _stop(self):
        """Stop the tool server and disconnect."""
        self._stop_connection()

        self.logger.info('Stopped server {name}'.format(name=self.name))

    # override, depending on server type
    def start(self):
        """Start the tool server."""
        pass

    # tools
    def initialize_tools(self):
        """Initialize tools for the tool server."""
        pass

    # override
    def add_tool(self, tool):
        """Add a tool to the server.

        Parameters:
            tool: Tool object to add.
        """
        pass

    # override
    def list_tools(self):
        """List available tools on the server.

        Returns:
            List of tools
        """
        return []
