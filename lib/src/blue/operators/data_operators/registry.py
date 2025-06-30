###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.utils import json_utils
from blue.tools.registry import ToolRegistry

###### Data Operator Clients
from blue.operators.data_operators.clients.local_client import LocalDataOperatorClient
from blue.operators.data_operators.clients.ray_client import RayDataOperatorClient

###############
### DataOperatorRegistry

class DataOperatorRegistry(ToolRegistry):
    def __init__(self, name="DATA_OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)
    ######### initialization, server, server description, server properties directly inherited from ToolRegistry

    ######### server /  data operator
    def register_server_operator(self, server, operator, description="", properties={}, rebuild=False):
        super().register_record(operator, 'operator', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def update_server_operator(self, server, operator, description=None, properties=None, rebuild=False):
        super().update_record(operator, 'operator', f'/server/{server}', description=description, properties=properties, rebuild=rebuild)

    def deregister_server_operator(self, server, operator, rebuild=False):
        record = self.get_server_operator(server, operator)
        super().deregister(record, rebuild=rebuild)

    def get_server_operators(self, server):
        return super().filter_record_contents(server, 'server', '/', filter_type='operator')

    def get_server_operator(self, server, operator):
        return super().filter_record_contents(server, 'server', '/', filter_type='operator', filter_name=operator, single=True)

    # description
    def get_server_operator_description(self, server, operator):
        return super().get_record_description(operator, 'operator', f'/server/{server}')

    def set_server_operator_description(self, server, operator, description, rebuild=False):
        super().set_record_description(operator, 'operator', f'/server/{server}', description, rebuild=rebuild)

    # properties
    def get_server_operator_properties(self, server, operator):
        return super().get_record_properties(operator, 'operator', f'/server/{server}')

    def get_server_operator_property(self, server, operator, key):
        return super().get_record_property(operator, 'operator', f'/server/{server}', key)

    def set_server_operator_property(self, server, operator, key, value, rebuild=False):
        super().set_record_property(operator, 'operator', f'/server/{server}', key, value, rebuild=rebuild)

    ######### sync
    # server connection (part of properties) inherited from ToolRegistry
    def connect_server(self, server):
        connection = None
        properties = self.get_server_properties(server)
        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]
                protocol = connection_properties.get("protocol")
                if protocol:
                    if protocol == "local":
                        connection = LocalDataOperatorClient(server, properties=properties)
                    elif protocol == "ray":
                        connection = RayDataOperatorClient(server, properties=properties)
                    # Add more protocols as needed
        return connection

    def execute_operator(self, operator, server, args, kwargs):
        connection = self.connect_server(server)
        if connection:
            return connection.execute_operator(operator, args, kwargs)
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

            # fetch operators
            fetched_operators = connection.fetch_operators()
            fetched_operators_set = set(fetched_operators)

            # get existing operators
            registry_operators = self.get_server_operators(server)
            registry_operators_set = set(json_utils.json_query(registry_operators, '$.name', single=False))

            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for operator in fetched_operators_set:
                if operator in registry_operators_set:
                    merges.add(operator)
                else:
                    adds.add(operator)
            for operator in registry_operators_set:
                if operator not in fetched_operators_set:
                    removes.add(operator)

            ## update operators in registry
            # add
            for operator in adds:
                self.register_server_operator(server, operator, description="", properties={}, rebuild=rebuild)

            # remove
            for operator in removes:
                self.deregister_server_operator(server, operator, rebuild=rebuild)

            ## recurse
            if recursive:
                for operator in fetched_operators_set:
                    self.sync_server_operator(server, operator, connection=connection, recursive=recursive, rebuild=rebuild)
            else:
                for operator in adds:
                    #  sync to update description, properties, schema
                    self.sync_server_operator(server, operator, connection=connection, recursive=False, rebuild=rebuild)

                for operator in merges:
                    #  sync to update description, properties, schema
                    self.sync_server_operator(server, operator, connection=connection, recursive=False, rebuild=rebuild)

    def sync_server_operator(self, server, operator, connection=None, recursive=False, rebuild=False):
        if connection is None:
            connection = self.connect_server(server)

        if connection:
            # fetch operator metadata
            metadata = connection.fetch_operator_metadata(operator)

            # update server operator properties
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

            self.update_server_operator(server, operator, description=description, properties=properties, rebuild=rebuild)

    ######## Methods not similar to ToolRegistry
    def register_local_data_operators(self, server_name="local", rebuild=True):
        properties = {
            "connection": {
                "protocol": "local"
            }
        }
        
        self.register_server(
            server_name, 
            created_by="system", 
            description="Local data operators server", 
            properties=properties, 
            rebuild=rebuild
        )
        
        self.sync_server(server_name, rebuild=rebuild)

    def get_all_operators(self):
        all_operators = []
        servers = self.get_servers()
        
        for server_record in servers:
            server_name = server_record.get('name')
            if server_name:
                operators = self.get_server_operators(server_name)
                for operator in operators:
                    operator['server'] = server_name
                    all_operators.append(operator)
        
        return all_operators

    def search_operators(self, keywords, server=None, approximate=False, hybrid=False, page=0, page_size=5, page_limit=10):
        scope = "/"
        if server:
            scope = f"/server/{server}"
        
        return super().search_records(
            keywords, 
            type="operator", 
            scope=scope, 
            approximate=approximate, 
            hybrid=hybrid, 
            page=page, 
            page_size=page_size, 
            page_limit=page_limit
        )
