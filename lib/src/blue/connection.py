###### Parsers, Utils
import logging

###### Backend, Databases
import redis

###### Blue
from blue.utils import uuid_utils


###############
### PooledConnectionFactory
#
class PooledConnectionFactory:
    __pool = None
    __pool_id = None

    def __init__(self, properties=None, decode_responses=True, use_instance_pool=False):
        self.properties = properties

        self.use_instance_pool = use_instance_pool
        self.decode_responses = decode_responses
        self._instance_pool = None

        # start connection pool
        self._start()

    def _start(self):
        # connectio details
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        # singleton connection from pool
        self.connection = None

        # max connections
        max_connections = None
        if "db.max_connections" in self.properties:
            max_connections = self.properties["db.max_connections"]

        if self.use_instance_pool:
            self._instance_pool = redis.ConnectionPool(
                host=host, port=port, max_connections=max_connections, decode_responses=self.decode_responses
            )
        else:
            if PooledConnectionFactory.__pool is None:
                PooledConnectionFactory.__pool_id = uuid_utils.create_uuid()
                PooledConnectionFactory.__pool = redis.ConnectionPool(
                    host=host, port=port, max_connections=max_connections, decode_responses=self.decode_responses
                )
    
    def get_id(self):
        return PooledConnectionFactory.__pool_id if not self.use_instance_pool else None

    def get_connection(self):
        if self.connection is None:
            pool = self._instance_pool if self.use_instance_pool else PooledConnectionFactory.__pool
            self.connection = redis.Redis(connection_pool=pool)
          
        return self.connection

    def count_in_use_connections(self):
        pool = self._instance_pool if self.use_instance_pool else PooledConnectionFactory.__pool
        return len(pool._in_use_connections)

    def count_created_connections(self):
        pool = self._instance_pool if self.use_instance_pool else PooledConnectionFactory.__pool
        return pool._created_connections
        
    def count_available_connections(self):
        pool = self._instance_pool if self.use_instance_pool else PooledConnectionFactory.__pool
        return len(pool._available_connections)
        
    def __repr__(self):
        return f"PooledConnectionManager(connection={self.connection}, pool_info=(created={self.count_created_connections()}, in_use={self.count_in_use_connections()}, available={self.count_available_connections()}))"
