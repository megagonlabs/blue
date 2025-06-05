###### Parsers, Formats, Utils
import argparse
import logging
import json


###### Blue
from blue.utils import json_utils
from blue.registry import Registry

###### Supported Tool Servers
from blue.tools.servers import RayServer
from blue.tools.servers import MCPServer


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
        server_connection = None

        properties = self.get_server_properties(server)

        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]

                protocol = connection_properties["protocol"]
                if protocol:
                    if protocol == "ray":
                        server_connection = RayServer(server, properties=properties)
                    elif protocol == "mcp":
                        server_connection = MCPServer(server, properties=properties)

        return server_connection

    def sync_all(self, recursive=False):
        # TODO
        pass

    def sync_server(self, server, recursive=False, rebuild=False):
        server_connection = self.connect_server(server)
        if server_connection:
            # fetch server metadata
            metadata = server_connection.fetch_metadata()

            # update server properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_server(server, description=description, properties=properties, rebuild=rebuild)

            # fetch tools
            fetched_tools = server_connection.fetch_tools()
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
                    self.sync_server_tool(server, tool, server_connection=server_connection, recursive=recursive, rebuild=rebuild)
            else:
                for tool in adds:
                    #  sync to update description, properties, schema
                    self.sync_server_tool(server, tool, server_connection=server_connection, recursive=False, rebuild=rebuild)

                for tool in merges:
                    #  sync to update description, properties, schema
                    self.sync_server_tool(server, tool, server_connection=server_connection, recursive=False, rebuild=rebuild)

    def sync_server_tool(self, server, tool, server_connection=None, recursive=False, rebuild=False):
        if server_connection is None:
            server_connection = self.connect_server(server)

        if server_connection:
            # fetch tool metadata
            metadata = server_connection.fetch_tool_metadata(tool)

            # update server tool properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_server_tool(server, tool, description=description, properties=properties, rebuild=rebuild)
