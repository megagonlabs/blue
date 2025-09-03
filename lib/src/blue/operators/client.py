###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging
from typing import List, Dict, Any

###### Blue
from blue.tools.client import ToolClient


###############
### OperatorClient


class OperatorClient(ToolClient):
    """
    Base client for operators following the same pattern as ToolClient.
    Handles validation, execution, and result formatting for operators.
    """

    def __init__(self, name: str = "OperatorClient", properties: Dict[str, Any] = None):
        super().__init__(name, properties=properties or {})

    ## _intialize, _start, _stop, _connect, _disconnect, _start_connection, _stop_connection, _initialize_properties, _update_properties inherited from ToolClient

    ######### server
    def fetch_metadata(self):
        return self.fetch_metadata()

    ######### operator
    def fetch_operators(self):
        return self.fetch_tools()

    def fetch_operator_metadata(self, operator):
        return self.fetch_tool_metadata(operator)

    def execute_operator(self, operator, args=None, kwargs=None):
        return self.execute_tool(operator, args=args, kwargs=kwargs)

    def refine_operator(self, operator, args=None, kwargs=None):
        return []

