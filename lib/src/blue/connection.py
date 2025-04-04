###### Parsers, Utils
import logging

###### Backend, Databases
import redis

###### Blue
from blue.utils import uuid_utils

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


###############
### PooledConnectionFactory
#
class PooledConnectionFactory:
    __pool = None
    __pool_id = None

    def __init__(self, properties=None):
        self.properties = properties

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

        # init class connection 
        if PooledConnectionFactory.__pool is None:
            PooledConnectionFactory.__pool_id = uuid_utils.create_uuid()
            PooledConnectionFactory.__pool = redis.connection.ConnectionPool(host=host, port=port, max_connections=max_connections, decode_responses=True)

    def get_id(self):
        return PooledConnectionFactory.__pool_id
    
    def get_connection(self):
        if self.connection is None:
            self.connection = redis.Redis(connection_pool=PooledConnectionFactory.__pool)

        return self.connection 

    def count_in_use_connections(self):
        return len(PooledConnectionFactory.__pool._in_use_connections)
    
    def count_created_connections(self):
        return PooledConnectionFactory.__pool._created_connections
    
    def count_available_connections(self):
        return len(PooledConnectionFactory.__pool._available_connections)

    def __repr__(self):
        return f"PooledConnectionManager(connection={self.connection}, pool_info=(created={self.count_created_connections()}, in_use={self.count_in_use_connections()}, available={self.count_available_connections()}))"
