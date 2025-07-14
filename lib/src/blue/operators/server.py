###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.operators.operator import Operator
from blue.tools.server import ToolServer
from blue.utils import log_utils


###############
### OperatorServer
#
class OperatorServer(ToolServer):
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    # opertors
    def initialize_operators(self):
        pass

    # override
    def add_operator(self, operator):
        pass

    # override
    def list_operators(self):
        return []
