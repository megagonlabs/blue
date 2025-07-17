###### Parsers, Formats, Utils
import argparse
import logging
import json


###### Blue
from blue.utils import json_utils
from blue.tools.registry import ToolRegistry

###### Supported Tool Clients
from blue.operators.clients.local_client import LocalOperatorClient
from blue.operators.clients.ray_client import RayOperatorClient
from blue.operators.clients.mcp_client import MCPOperatorClient

###### Local, Ray Operators
from blue.operators.clients import local_operators, ray_operators


###############
### OperatorRegistry
#
class OperatorRegistry(ToolRegistry):
    def __init__(self, name="OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ######### server/operator
    def register_server_operator(self, server, operator, description="", properties={}, rebuild=False):
        super().register_record(operator, 'operator', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def register_server_tool(self, server, tool, description="", properties={}, rebuild=False):
        self.register_server_operator(server, tool, description=description, properties=properties, rebuild=rebuild)

    def update_server_operator(self, server, operator, description=None, properties=None, rebuild=False):
        super().update_record(operator, 'operator', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def update_server_tool(self, server, tool, description=None, properties=None, rebuild=False):
        self.update_server_operator(server, tool, description=description, properties=properties, rebuild=rebuild)

    def deregister_server_operator(self, server, operator, rebuild=False):
        record = self.get_server_operator(server, operator)
        super().deregister(record, rebuild=rebuild)

    def deregister_server_tool(self, server, tool, rebuild=False):
        self.deregister_server_operator(server, tool, rebuild=rebuild)

    def get_server_operators(self, server):
        return super().filter_record_contents(server, 'server', '/', filter_type='operator')

    def get_server_tools(self, server):
        return self.get_server_operators(server)

    def get_server_operator(self, server, operator):
        return super().filter_record_contents(server, 'server', '/', filter_type='operator', filter_name=operator, single=True)

    def get_server_tool(self, server, tool):
        return self.get_server_operator(server, tool)

    # description
    def get_server_operator_description(self, server, operator):
        return super().get_record_description(operator, 'operator', f'/server/{server}')

    def get_server_tool_description(self, server, tool):
        return self.get_server_operator_description(server, tool)

    def set_server_operator_description(self, server, operator, description, rebuild=False):
        super().set_record_description(operator, 'operator', f'/server/{server}', description, rebuild=rebuild)

    def set_server_tool_description(self, server, tool, description, rebuild=False):
        self.set_server_operator_description(server, tool, description, rebuild=rebuild)

    # properties
    def get_server_operator_properties(self, server, operator):
        return super().get_record_properties(operator, 'operator', f'/server/{server}')

    def get_server_tool_properties(self, server, tool):
        return self.get_server_operator_properties(server, tool)

    def get_server_operator_property(self, server, operator, key):
        return super().get_record_property(operator, 'operator', f'/server/{server}', key)

    def get_server_tool_property(self, server, tool, key):
        return self.get_server_operator_property(server, tool, key)

    def set_server_operator_property(self, server, operator, key, value, rebuild=False):
        super().set_record_property(operator, 'operator', f'/server/{server}', key, value, rebuild=rebuild)

    def set_server_tool_property(self, server, tool, key, value, rebuild=False):
        self.set_server_operator_property(server, tool, key, value, rebuild=rebuild)

    ######### sync
    def connect_server(self, server):
        connection = None

        properties = self.get_server_properties(server)

        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]

                protocol = connection_properties["protocol"]
                if protocol:
                    if protocol == "local":
                        connection = LocalOperatorClient(server, operators=local_operators.operators_dict, properties=properties)
                    elif protocol == "ray":
                        connection = RayOperatorClient(server, operators=ray_operators.operators_dict, properties=properties)
                    elif protocol == "mcp":
                        connection = MCPOperatorClient(server, properties=properties)

        return connection

    def execute_operator(self, operator, server, args, kwargs):
        connection = self.connect_server(server)
        if connection:
            return connection.execute_operator(operator, args, kwargs)
        else:
            return None

    def execute_tool(self, tool, server, args, kwargs):
        return self.execute_operator(tool, server, args, kwargs)
