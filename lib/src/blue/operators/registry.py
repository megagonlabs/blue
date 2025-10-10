###### Parsers, Formats, Utils
import argparse
import logging
import json


###### Blue
from blue.utils import json_utils
from blue.tools.registry import ToolRegistry


###############
### OperatorRegistry
#
class OperatorRegistry(ToolRegistry):
    def __init__(self, name="OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        """
        Initialize the OperatorRegistry.

        Parameters:
            name (str): Registry name. Default is "OPERATOR_REGISTRY".
            id (str, optional): Unique registry ID.
            sid (str, optional): Session ID.
            cid (str, optional): Context ID.
            prefix (str, optional): Registry key prefix.
            suffix (str, optional): Registry key suffix.
            properties (dict, optional): Additional registry configuration properties.
        """
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ######### server/operator
    def register_server_operator(self, server, operator, description="", properties={}, rebuild=False):
        """
        Register a new operator under a specific server.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            description (str, optional): Description of the operator.
            properties (dict, optional): Operator metadata and configuration.
            rebuild (bool, optional): Whether to rebuild the search index after registration.
        """
        super().register_record(operator, 'operator', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def register_server_tool(self, server, tool, description="", properties={}, rebuild=False):
        """
        Alias for `register_server_operator`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.
            description (str, optional): Description of the tool.
            properties (dict, optional): Tool metadata and configuration.
            rebuild (bool, optional): Whether to rebuild the search index.
        """
        self.register_server_operator(server, tool, description=description, properties=properties, rebuild=rebuild)

    def update_server_operator(self, server, operator, description=None, icon=None, properties=None, rebuild=False):
        """
        Update the metadata or properties of an existing operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            description (str, optional): New description text.
            icon (str, optional): Icon or visual identifier.
            properties (dict, optional): Updated property dictionary.
            rebuild (bool, optional): Whether to rebuild the index after update.
        """
        super().update_record(operator, 'operator', f'/server/{server}', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def update_server_tool(self, server, tool, description=None, properties=None, rebuild=False):
        """
        Alias for `update_server_operator`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.
            description (str, optional): New description text.
            properties (dict, optional): Updated properties.
            rebuild (bool, optional): Whether to rebuild the index.
        """
        self.update_server_operator(server, tool, description=description, properties=properties, rebuild=rebuild)

    def deregister_server_operator(self, server, operator, rebuild=False):
        """
        Deregister (remove) an operator from a specific server.

        Parameters:
            server (str): Server name.
            operator (str): Operator name to remove.
            rebuild (bool, optional): Whether to rebuild the search index.
        """
        record = self.get_server_operator(server, operator)
        super().deregister(record, rebuild=rebuild)

    def deregister_server_tool(self, server, tool, rebuild=False):
        """
        Alias for `deregister_server_operator`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name to remove.
            rebuild (bool, optional): Whether to rebuild the index.
        """
        self.deregister_server_operator(server, tool, rebuild=rebuild)

    def get_server_operators(self, server):
        """
        List all operators registered under a given server.

        Parameters:
            server (str): Server name.

        Returns:
            list[dict]: List of operator records.
        """
        return super().filter_record_contents(server, 'server', '/', filter_type='operator')

    def get_server_tools(self, server):
        """
        Alias for `get_server_operators`.

        Parameters:
            server (str): Server name.

        Returns:
            list[dict]: List of tools registered under the server.
        """
        return self.get_server_operators(server)

    def get_server_operator(self, server, operator):
        """
        Retrieve a single operator record from a given server.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.

        Returns:
            dict | None: Operator record if found, otherwise None.
        """
        return super().filter_record_contents(server, 'server', '/', filter_type='operator', filter_name=operator, single=True)

    def get_server_tool(self, server, tool):
        """
        Alias for `get_server_operator`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.

        Returns:
            dict | None: Tool record if found.
        """
        return self.get_server_operator(server, tool)

    # description
    def get_server_operator_description(self, server, operator):
        """
        Retrieve the description text of a specific operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.

        Returns:
            str | None: Description if available.
        """
        return super().get_record_description(operator, 'operator', f'/server/{server}')

    def get_server_tool_description(self, server, tool):
        """
        Alias for `get_server_operator_description`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.

        Returns:
            str | None: Description text if found.
        """
        return self.get_server_operator_description(server, tool)

    def set_server_operator_description(self, server, operator, description, rebuild=False):
        """
        Update the description of a server operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            description (str): New description text.
            rebuild (bool, optional): Whether to rebuild the search index.
        """
        super().set_record_description(operator, 'operator', f'/server/{server}', description, rebuild=rebuild)

    def set_server_tool_description(self, server, tool, description, rebuild=False):
        """
        Alias for `set_server_operator_description`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.
            description (str): New description text.
            rebuild (bool, optional): Whether to rebuild the index.
        """
        self.set_server_operator_description(server, tool, description, rebuild=rebuild)

    # properties
    def get_server_operator_properties(self, server, operator):
        """
        Get the properties dictionary of a specific server operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.

        Returns:
            dict | None: Operator properties.
        """
        return super().get_record_properties(operator, 'operator', f'/server/{server}')

    def get_server_tool_properties(self, server, tool):
        """
        Alias for `get_server_operator_properties`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.

        Returns:
            dict | None: Tool properties.
        """
        return self.get_server_operator_properties(server, tool)

    def get_server_operator_property(self, server, operator, key):
        """
        Retrieve a single property value of a server operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            key (str): Property key.

        Returns:
            Any: Property value if found, else None.
        """
        return super().get_record_property(operator, 'operator', f'/server/{server}', key)

    def delete_server_operator_property(self, server, operator, key, rebuild=False):
        """
        Delete a specific property from a server operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            key (str): Property key to remove.
            rebuild (bool, optional): Whether to rebuild the index after deletion.
        """
        super().delete_record_property(operator, 'operator', f'/server/{server}', key, rebuild=rebuild)

    def get_server_tool_property(self, server, tool, key):
        """
        Alias for `get_server_operator_property`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.
            key (str): Property key.

        Returns:
            Any: Property value if found.
        """
        return self.get_server_operator_property(server, tool, key)

    def set_server_operator_property(self, server, operator, key, value, rebuild=False):
        """
        Set or update a property of a server operator.

        Parameters:
            server (str): Server name.
            operator (str): Operator name.
            key (str): Property key.
            value (Any): Property value.
            rebuild (bool, optional): Whether to rebuild the index.
        """
        super().set_record_property(operator, 'operator', f'/server/{server}', key, value, rebuild=rebuild)

    def set_server_tool_property(self, server, tool, key, value, rebuild=False):
        """
        Alias for `set_server_operator_property`.

        Parameters:
            server (str): Server name.
            tool (str): Tool name.
            key (str): Property key.
            value (Any): Property value.
            rebuild (bool, optional): Whether to rebuild the index.
        """
        self.set_server_operator_property(server, tool, key, value, rebuild=rebuild)

    ######### sync
    def connect_server(self, server):
        """
        Establish a client connection to a given server.

        The connection protocol is determined from the server's stored
        properties under the "connection" key. Supported protocols include:
        - `local`
        - `ray`
        - `mcp`

        Parameters:
            server (str): Server name.

        Returns:
            object | None: Operator client instance if successful, else None.
        """
        connection = None

        properties = self.get_server_properties(server)

        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]

                protocol = connection_properties["protocol"]
                if protocol:
                    if protocol == "local":
                        # import on demand
                        from blue.operators.clients.local_client import LocalOperatorClient
                        from blue.operators.clients import local_operators

                        connection = LocalOperatorClient(server, operators=local_operators.operators_dict, properties=properties)
                    elif protocol == "ray":
                        from blue.operators.clients.ray_client import RayOperatorClient
                        from blue.operators.clients import ray_operators

                        connection = RayOperatorClient(server, operators=ray_operators.operators_dict, properties=properties)
                    elif protocol == "mcp":
                        from blue.operators.clients.mcp_client import MCPOperatorClient

                        connection = MCPOperatorClient(server, properties=properties)

        return connection

    def execute_operator(self, operator, server, args, kwargs):
        """
        Execute a remote operator on a specific server.

        Parameters:
            operator (str): Operator name.
            server (str): Server name.
            args (list): Positional arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            Any: Operator execution result, or None if connection unavailable.
        """
        connection = self.connect_server(server)
        if connection:
            return connection.execute_operator(operator, args, kwargs)
        else:
            return None

    def execute_tool(self, tool, server, args, kwargs):
        """
        Alias for `execute_operator`.

        Parameters:
            tool (str): Tool name.
            server (str): Server name.
            args (list): Positional arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            Any: Tool execution result, or None if connection unavailable.
        """
        return self.execute_operator(tool, server, args, kwargs)

    def refine_operator(self, operator, server, args, kwargs):
        """
        Refine or adjust operator output using a remote server connection.

        Parameters:
            operator (str): Operator name.
            server (str): Server name.
            args (list): Positional arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            list: Refined operator output, or empty list if unavailable.
        """
        connection = self.connect_server(server)
        if connection:
            return connection.refine_operator(operator, args, kwargs)
        else:
            return []

    def get_operator_attributes(self, operator, server):
        """
        Retrieve metadata or attributes of a given operator from a connected server.

        Parameters:
            operator (str): Operator name.
            server (str): Server name.

        Returns:
            list: List of operator attributes, or empty list if unavailable.
        """
        connection = self.connect_server(server)
        if connection:
            return connection.get_operator_attributes(operator)
        else:
            return []
