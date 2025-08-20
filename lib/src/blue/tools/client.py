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

        # connection properties
        self._initialize_connection_properties()

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_connection_properties(self):
        connection_properties = {}

        connection_properties['protocol'] = 'default'
        self.properties['connection'] = connection_properties

    def _initialize_logger(self):
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("tool_client", self.name, -1)

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

        self.logger.info('Started server {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        self.logger.info('Stopped server {name}'.format(name=self.name))

    ######### server
    def fetch_metadata(self):
        return {}

    ######### tool
    def fetch_tools(self):
        return []

    def fetch_tool_metadata(self, tool):
        return {}

    def execute_tool(self, tool, args, kwargs):
        return [{}]
