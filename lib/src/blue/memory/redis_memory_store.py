from blue.memory.memory_store import MemoryStore
from blue.connection import PooledConnectionFactory
from typing import List, Dict, Optional
import json


class RedisMemoryStore(MemoryStore):
    """
    Redis implementation using PooledConnectionFactory.
    Implements optimized storage using hash (data, index) and sorted set (time).
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

    # key helpers
    def _get_data_key(self, base_key: str) -> str:
        return f"{base_key}:DATA"

    def _get_key_index_key(self, base_key: str) -> str:
        return f"{base_key}:INDEX:KEYS"

    def _get_time_index_key(self, base_key: str) -> str:
        return f"{base_key}:INDEX:TIME"

    # optimized implementation
    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
        try:
            # store data (hash)
            self.connection.hset(self._get_data_key(base_key), entry_id, json.dumps(entry))
            # update key index (hash)
            if custom_key:
                self.connection.hset(self._get_key_index_key(base_key), custom_key, entry_id)
            # update time index (sorted set)
            self.connection.zadd(self._get_time_index_key(base_key), {entry_id: timestamp})
        except Exception as ex:
            raise ex

    def get_entry_by_id(self, base_key: str, entry_id: str) -> Optional[Dict]:
        try:
            result = self.connection.hget(self._get_data_key(base_key), entry_id)
            return json.loads(result) if result else None
        except Exception as ex:
            raise ex

    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
        try:
            # get ID from index
            entry_id = self.connection.hget(self._get_key_index_key(base_key), custom_key)
            if not entry_id:
                return None
            # get data using ID
            return self.get_entry_by_id(base_key, entry_id)
        except Exception as ex:
            raise ex

    def get_entries_by_time_range(self, base_key: str, start: float, end: float) -> List[Dict]:
        try:
            # get IDs from sorted set
            entry_ids = self.connection.zrangebyscore(self._get_time_index_key(base_key), start, end)
            if not entry_ids:
                return []
            # batch get data (HMGET)
            result = self.connection.hmget(self._get_data_key(base_key), entry_ids)
            return [json.loads(v) for v in result if v]
        except Exception as ex:
            raise ex
