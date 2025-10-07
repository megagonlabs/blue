###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.utils import log_utils


###############
### ToolClient
#
class ToolClient:
    """A ToolClient connects to a ToolServer and interfaces with its tools"""

    def __init__(self, name, properties={}):
        """Initialize a ToolClient instance.

        Parameters:
            name: Name of the tool client
            properties (dict): Properties of the tool client
        """
        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """Initialize the tool client with properties and logger.

        Parameters:
            properties: Properties to override default properties.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default properties for tool client."""
        self.properties = {}

        # connection properties
        self._initialize_connection_properties()

    def _update_properties(self, properties=None):
        """Update properties with given properties.

        Parameters:
            properties: Properties to override default properties.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_connection_properties(self):
        """Initialize default connection properties."""
        connection_properties = {}

        connection_properties['protocol'] = 'default'
        self.properties['connection'] = connection_properties

    def _initialize_logger(self):
        """Initialize logger for the tool client."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("tool_client", self.name, -1)

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

        self.logger.info('Started server {name}'.format(name=self.name))

    def _stop(self):
        """Stop the tool server and disconnect."""
        self._stop_connection()

        self.logger.info('Stopped server {name}'.format(name=self.name))

    ######### server
    def fetch_metadata(self):
        """Fetch metadata from the tool server.

        Returns:
            Metadata dictionary
        """
        return {}

    ######### tool
    def fetch_tools(self):
        """Fetch list of available tools from the tool server.

        Returns:
            List of tools
        """
        return []

    def fetch_tool_metadata(self, tool):
        """Fetch metadata for a specific tool from the tool server.

        Parameters:
            tool: Name of the tool

        Returns:
            Metadata dictionary for the tool
        """
        return {}

    def execute_tool(self, tool, args, kwargs):
        """Execute a specific tool on the tool server.

        Parameters:
            tool: Name of the tool
            args: Args for the tool function
            kwargs: Keyword args for the tool function

        Returns:

        """
        return [{}]
