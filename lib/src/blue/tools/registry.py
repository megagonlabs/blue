###### Parsers, Formats, Utils
import argparse
import logging
import json


###### Blue
from blue.utils import json_utils
from blue.registry import Registry


###############
### ToolRegistry
#
class ToolRegistry(Registry):
    """A ToolRegistry manages tool servers and their tools"""

    def __init__(self, name="TOOL_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        """Instantiate a ToolRegistry object.

        Parameters:
            name: Name of the tool registry. Defaults to "TOOL_REGISTRY".
            id: ID of the tool registry. Defaults to None.
            sid: SID (Short ID) of the tool registry. Defaults to None.
            cid: CID (Canonical ID) of the tool registry. Defaults to None.
            prefix: Prefix for the tool registry. Defaults to None.
            suffix: Suffix for the tool registry. Defaults to None.
            properties: Properties of the tool registry. Defaults to {}.
        """
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        """Initialize default properties for tool registry."""
        super()._initialize_properties()

    ######### server
    def register_server(self, server, created_by, description="", properties={}, rebuild=False):
        """Register a tool server to the registry.

        Parameters:
            server: Name of the tool server
            created_by: Creator of the tool server
            description: Description of the tool server. Defaults to "".
            properties: Properties of the tool server. Defaults to {}.
            rebuild: Whether to rebuild the registry index after registration. Defaults to False.
        """
        super().register_record(server, 'server', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_server(self, server, description=None, icon=None, properties=None, rebuild=False):
        """Update a tool server entry in the registry.

        Parameters:
            server: Name of the tool server
            description: Description of the tool server. Defaults to None.
            icon: Icon for the tool server. Defaults to None.
            properties: Properties of the tool server. Defaults to None.
            rebuild: Whether to rebuild the registry index after update. Defaults to False.
        """
        super().update_record(server, 'server', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def deregister_server(self, server, rebuild=False):
        """Deregister a tool server from the registry.

        Parameters:
            server: Name of the tool server
            rebuild: Whether to rebuild the registry index after deregistration. Defaults to False.
        """
        record = self.get_server(server)
        super().deregister(record, rebuild=rebuild)

    def get_servers(self):
        """Get all registered tool servers.

        Returns:
            List of registered tool servers
        """
        return super().list_records(type="server", scope="/")

    def get_server(self, server):
        """Get a specific registered tool server metadata.

        Parameters:
            server: Name of the tool server

        Returns:
            Metadata of the specified tool server
        """
        return super().get_record(server, 'server', '/')

    # description
    def get_server_description(self, server):
        """Get the description of a specific registered tool server.

        Parameters:
            server: Name of the tool server

        Returns:
            (str): Description of the specified tool server
        """
        return super().get_record_description(server, 'server', '/')

    def set_server_description(self, server, description, rebuild=False):
        """Set the description of a specific registered tool server.

        Parameters:
            server: Name of the tool server
            description (str): New description for the tool server
            rebuild (bool): Whether to rebuild the registry index after setting the new description. Defaults to False.
        """
        super().set_record_description(server, 'server', '/', description, rebuild=rebuild)

    # properties
    def get_server_properties(self, server):
        """Get the properties of a specific registered tool server.

        Parameters:
            server: Name of the tool server

        Returns:
            Properties of the specified tool server
        """
        return super().get_record_properties(server, 'server', '/')

    def get_server_property(self, server, key):
        """Get a specific property of a registered tool server.

        Parameters:
            server: Name of the tool server
            key (str): Property key

        Returns:
            (Any): Value of the specified property key for the tool server
        """
        return super().get_record_property(server, 'server', '/', key)

    def set_server_property(self, server, key, value, rebuild=False):
        """Set a specific property of a registered tool server.

        Parameters:
            server: Name of the tool server
            key (str): Key of the property to set
            value (Any): Value of the property to set
            rebuild (bool): Whether to rebuild the registry index after setting the property. Defaults to False.
        """
        super().set_record_property(server, 'server', '/', key, value, rebuild=rebuild)

    def delete_server_property(self, server, key, rebuild=False):
        """Delete a specific property of a registered tool server.

        Parameters:
            server: Name of the tool server
            key (str): Key of the property to delete
            rebuild (bool): Whether to rebuild the registry index after deleting the property. Defaults to False.
        """
        super().delete_record_property(server, 'server', '/', key, rebuild=rebuild)

    ######### server/tool
    def register_server_tool(self, server, tool, description="", properties={}, rebuild=False):
        """Register a tool under a specific tool server in the registry.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            description (str): Description of the tool. Defaults to "".
            properties: Properties of the tool. Defaults to {}.
            rebuild (bool): Whether to rebuild the registry index after registration of the tool. Defaults to False.
        """
        super().register_record(tool, 'tool', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def update_server_tool(self, server, tool, description=None, properties=None, rebuild=False):
        """Update a tool entry under a specific tool server in the registry.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            description (str): Description of the tool. Defaults to None.
            properties: Properties of the tool. Defaults to None.
            rebuild (bool): Whether to rebuild the registry index after update of the tool. Defaults to False.
        """
        super().update_record(tool, 'tool', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def deregister_server_tool(self, server, tool, rebuild=False):
        """Deregister a tool from under a specific tool server in the registry.

        Parameters:
            server: Name of the tool server
            tool: Tool to deregister
            rebuild (bool): Whether to rebuild the registry index after deregistration of the tool. Defaults to False.
        """
        record = self.get_server_tool(server, tool)
        super().deregister(record, rebuild=rebuild)

    def get_server_tools(self, server):
        """Get all registered tools under a specific tool server.

        Parameters:
            server: Name of the tool server

        Returns:
            List of registered tools under the specified tool server
        """
        return super().filter_record_contents(server, 'server', '/', filter_type='tool')

    def get_server_tool(self, server, tool):
        """Get a specific registered tool metadata under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool

        Returns:
            Metadata of the specified tool under the specified tool server
        """
        return super().filter_record_contents(server, 'server', '/', filter_type='tool', filter_name=tool, single=True)

    # description
    def get_server_tool_description(self, server, tool):
        """Get the description of a specific registered tool under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool

        Returns:
            (str): Description of the specified tool under the specified tool server
        """
        return super().get_record_description(tool, 'tool', f'/server/{server}')

    def set_server_tool_description(self, server, tool, description, rebuild=False):
        """Set the description of a specific registered tool under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            description (str): New description for the tool
            rebuild (bool): Whether to rebuild the registry index after setting the new description for the tool. Defaults to False.
        """
        super().set_record_description(tool, 'tool', f'/server/{server}', description, rebuild=rebuild)

    # properties
    def get_server_tool_properties(self, server, tool):
        """Get the properties of a specific registered tool under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool

        Returns:
            Properties of the specified tool under the specified tool server
        """
        return super().get_record_properties(tool, 'tool', f'/server/{server}')

    def get_server_tool_property(self, server, tool, key):
        """Get a specific property of a registered tool under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            key (str): Property key

        Returns:
            (Any): Value of the specified property key for the tool under the specified tool server
        """
        return super().get_record_property(tool, 'tool', f'/server/{server}', key)

    def set_server_tool_property(self, server, tool, key, value, rebuild=False):
        """Set a specific property of a registered tool under a specific tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            key (str): Key of the property to set
            value (Any): Value of the property to set
            rebuild (bool): Whether to rebuild the registry index after setting the property. Defaults to False.
        """
        super().set_record_property(tool, 'tool', f'/server/{server}', key, value, rebuild=rebuild)

    ######### sync
    # server connection (part of properties)
    def get_server_connection(self, server):
        """Get the connection properties of a specific registered tool server.

        Parameters:
            server: Name of the tool server

        Returns:
            Connection properties of the specified tool server
        """
        return self.get_server_property(server, 'connection')

    def set_server_connection(self, server, connection, rebuild=False):
        """Set the connection properties of a specific registered tool server.

        Parameters:
            server: Name of the tool server
            connection: Connection properties to set
            rebuild (bool): Whether to rebuild the registry index after setting the connection properties. Defaults to False.
        """
        self.set_server_property(server, 'connection', connection, rebuild=rebuild)

    def connect_server(self, server):
        """Connect to a specific registered tool server.

        Parameters:
            server: Name of the tool server

        Returns:
            Connection object to the specified tool server or None
        """
        connection = None

        properties = self.get_server_properties(server)

        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]

                protocol = connection_properties["protocol"]
                if protocol:
                    if protocol == "local":
                        from blue.tools.clients.local_client import LocalToolClient
                        from blue.tools.clients import local_tools

                        connection = LocalToolClient(server, tools=local_tools.tools_dict, properties=properties)
                    elif protocol == "ray":
                        from blue.tools.clients.ray_client import RayToolClient
                        from blue.tools.clients import ray_tools

                        connection = RayToolClient(server, tools=ray_tools.tools_dict, properties=properties)
                    elif protocol == "mcp":
                        from blue.tools.clients.mcp_client import MCPToolClient

                        connection = MCPToolClient(server, properties=properties)

        return connection

    def execute_tool(self, tool, server, args, kwargs):
        """Execute a specific tool on a specific registered tool server.

        Parameters:
            tool: Name of the tool
            server: Name of the tool server
            args: Arguments for the tool function
            kwargs: Keyword arguments for the tool function

        Returns:
            Result of the tool execution or None
        """
        connection = self.connect_server(server)
        if connection:
            return connection.execute_tool(tool, args, kwargs)
        else:
            return None

    def sync_all(self, recursive=False):
        """Sync all registered tool servers and their tools.

        Parameters:
            recursive (bool): Whether to recursively sync tools. Defaults to False.
        """
        # TODO
        pass

    def sync_server(self, server, recursive=False, rebuild=False):
        """Sync a specific registered tool server and its tools.

        Parameters:
            server: Name of the tool server
            recursive (bool): Whether to recursively sync tools. Defaults to False.
            rebuild (bool): Whether to rebuild the registry index after syncing. Defaults to False.
        """
        connection = self.connect_server(server)
        if connection:
            # fetch server metadata
            metadata = connection.fetch_metadata()

            # update server properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_server(server, description=description, properties=properties, rebuild=rebuild)

            # fetch tools
            fetched_tools = connection.fetch_tools()
            fetched_tools_set = set(fetched_tools)

            # get existing tools
            registry_tools = self.get_server_tools(server)
            registry_tools_set = set(json_utils.json_query(registry_tools, '$.name', single=False))

            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for tool in fetched_tools_set:
                if tool in registry_tools_set:
                    merges.add(tool)
                else:
                    adds.add(tool)
            for tool in registry_tools_set:
                if tool not in fetched_tools_set:
                    removes.add(tool)

            # update registry
            # add
            for tool in adds:
                self.register_server_tool(server, tool, description="", properties={}, rebuild=rebuild)

            # remove
            for tool in removes:
                self.deregister_server_tool(server, tool, rebuild=rebuild)

            ## recurse
            if recursive:
                for tool in fetched_tools_set:
                    self.sync_server_tool(server, tool, connection=connection, recursive=recursive, rebuild=rebuild)
            else:
                for tool in adds:
                    #  sync to update description, properties, schema
                    self.sync_server_tool(server, tool, connection=connection, recursive=False, rebuild=rebuild)

                for tool in merges:
                    #  sync to update description, properties, schema
                    self.sync_server_tool(server, tool, connection=connection, recursive=False, rebuild=rebuild)

    def sync_server_tool(self, server, tool, connection=None, recursive=False, rebuild=False):
        """Sync a specific tool under a specific registered tool server.

        Parameters:
            server: Name of the tool server
            tool: Name of the tool
            connection: Connection object to the tool server. If None, a new connection will be established. Defaults to None.
            recursive (bool): Whether to recursively sync. Defaults to False.
            rebuild (bool): Whether to rebuild the registry index after syncing. Defaults to False.
        """
        if connection is None:
            connection = self.connect_server(server)

        if connection:
            # fetch tool metadata
            metadata = connection.fetch_tool_metadata(tool)

            # update server tool properties
            description = ""
            if 'description' in metadata:
                description = metadata['description']
                del metadata['description']
            properties = {}
            if 'properties' in metadata:
                properties = metadata['properties']
                del metadata['properties']

            # add remaining as metadata
            if 'name' in metadata:
                del metadata['name']
            properties['metadata'] = metadata

            self.update_server_tool(server, tool, description=description, properties=properties, rebuild=rebuild)
