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
    def __init__(self, name="TOOL_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

    ######### server
    def register_server(self, server, created_by, description="", properties={}, rebuild=False):
        super().register_record(server, 'server', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_server(self, server, description=None, icon=None, properties=None, rebuild=False):
        super().update_record(server, 'server', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def deregister_server(self, server, rebuild=False):
        record = self.get_server(server)
        super().deregister(record, rebuild=rebuild)

    def get_servers(self):
        return super().list_records(type="server", scope="/")

    def get_server(self, server):
        return super().get_record(server, 'server', '/')

    # description
    def get_server_description(self, server):
        return super().get_record_description(server, 'server', '/')

    def set_server_description(self, server, description, rebuild=False):
        super().set_record_description(server, 'server', '/', description, rebuild=rebuild)

    # properties
    def get_server_properties(self, server):
        return super().get_record_properties(server, 'server', '/')

    def get_server_property(self, server, key):
        return super().get_record_property(server, 'server', '/', key)

    def set_server_property(self, server, key, value, rebuild=False):
        super().set_record_property(server, 'server', '/', key, value, rebuild=rebuild)

    def delete_server_property(self, server, key, rebuild=False):
        super().delete_record_property(server, 'server', '/', key, rebuild=rebuild)

    ######### server/tool
    def register_server_tool(self, server, tool, description="", properties={}, rebuild=False):
        super().register_record(tool, 'tool', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def update_server_tool(self, server, tool, description=None, properties=None, rebuild=False):
        super().update_record(tool, 'tool', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def deregister_server_tool(self, server, tool, rebuild=False):
        record = self.get_server_tool(server, tool)
        super().deregister(record, rebuild=rebuild)

    def get_server_tools(self, server):
        return super().filter_record_contents(server, 'server', '/', filter_type='tool')

    def get_server_tool(self, server, tool):
        return super().filter_record_contents(server, 'server', '/', filter_type='tool', filter_name=tool, single=True)

    # description
    def get_server_tool_description(self, server, tool):
        return super().get_record_description(tool, 'tool', f'/server/{server}')

    def set_server_tool_description(self, server, tool, description, rebuild=False):
        super().set_record_description(tool, 'tool', f'/server/{server}', description, rebuild=rebuild)

    # properties
    def get_server_tool_properties(self, server, tool):
        return super().get_record_properties(tool, 'tool', f'/server/{server}')

    def get_server_tool_property(self, server, tool, key):
        return super().get_record_property(tool, 'tool', f'/server/{server}', key)

    def set_server_tool_property(self, server, tool, key, value, rebuild=False):
        super().set_record_property(tool, 'tool', f'/server/{server}', key, value, rebuild=rebuild)

    ######### sync
    # server connection (part of properties)
    def get_server_connection(self, server):
        return self.get_server_property(server, 'connection')

    def set_server_connection(self, server, connection, rebuild=False):
        self.set_server_property(server, 'connection', connection, rebuild=rebuild)

    def connect_server(self, server):
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
        connection = self.connect_server(server)
        if connection:
            return connection.execute_tool(tool, args, kwargs)
        else:
            return None

    def sync_all(self, recursive=False):
        # TODO
        pass

    def sync_server(self, server, recursive=False, rebuild=False):
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
