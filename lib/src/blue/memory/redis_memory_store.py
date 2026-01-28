from blue.memory.memory_store import MemoryStore
from blue.connection import PooledConnectionFactory
from typing import List, Dict


class RedisMemoryStore(MemoryStore):
    """
    Redis implementation using PooledConnectionFactory.
    """

    def __init__(self, properties: Dict):
        self.properties = properties
        self.connection_factory = None
        self.connection = None

    def initialize(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def append_to_list(self, key: str, entry: Dict) -> bool:
        try:
            self.connection.json().set(key, "$", [], nx=True)
            self.connection.json().arrappend(key, "$", entry)
        except Exception as ex:
            raise ex

    def get_list(self, key: str) -> List[Dict]:
        if not self.connection.exists(key):
            return []
        try:
            data = self.connection.json().get(key)
            return data if data else []
        except Exception as ex:
            raise ex

    def exists(self, key: str) -> bool:
        return self.connection.exists(key)
