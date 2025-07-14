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
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
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
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("tool_server", self.name, -1)

    ###### connection
    def _start_connection(self):
        connection = self.properties['connection']

        self.connection = self._connect(**connection)

    def _stop_connection(self):
        self._disconnect()

    def _connect(self, **connection):
        return None

    def _disconnect(self):
        return None

    def _start(self):
        # self.logger.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize tools
        self.initialize_tools()

        self.logger.info('Started server {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        self.logger.info('Stopped server {name}'.format(name=self.name))

    # override, depending on server type
    def start(self):
        pass

    # tools
    def initialize_tools(self):
        pass

    # override
    def add_tool(self, tool):
        pass

    # override
    def list_tools(self):
        return []
