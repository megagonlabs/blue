from blue.memories.memory_store import MemoryStore
from blue.connection import PooledConnectionFactory
from typing import List, Dict, Optional
import json


class RedisMemoryStore(MemoryStore):
    """
    Redis implementation of the MemoryStore interface using PooledConnectionFactory.

    This class provides optimized storage mechanisms for retrieving data by direct ID,
    secondary key index, or time ranges. It utilizes specific Redis data structures
    for performance:
    - **Hashes**: For storing the actual data payload and the secondary key index.
    - **Sorted Sets (ZSET)**: For time-series indexing.
    - **RedisJSON**: For list-based storage operations.

    Attributes:
        properties (Dict): Configuration properties for the Redis connection.
        connection_factory (PooledConnectionFactory): Factory instance to manage Redis connections.
        connection: The active Redis client instance.
    """

    def __init__(self, properties: Dict):
        """
        Initialize the RedisMemoryStore.

        Parameters:
            properties (Dict): Dictionary containing connection details (host, port, etc.)
                passed to the `PooledConnectionFactory`.
        """
        self.properties = properties
        self.connection_factory = None
        self.connection = None

    def initialize(self):
        """
        Sets up the connection factory and establishes the Redis connection.
        """
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def append_to_list(self, key: str, entry: Dict) -> bool:
        """
        Appends a dictionary entry to a JSON list stored at the specified key.
        Uses RedisJSON (`JSON.ARRAPPEND`).

        Parameters:
            key (str): The Redis key where the list is stored.
            entry (Dict): The data to append.

        Returns:
            bool: Always returns None (implicitly), but raises exception on failure.

        Raises:
            Exception: If the Redis operation fails.
        """
        try:
            self.connection.json().set(key, "$", [], nx=True)
            self.connection.json().arrappend(key, "$", entry)
        except Exception as ex:
            raise ex

    def get_list(self, key: str) -> List[Dict]:
        """
        Retrieves the full list of dictionaries stored at the specified key.
        Uses RedisJSON (`JSON.GET`).

        Parameters:
            key (str): The Redis key to retrieve.

        Returns:
            List[Dict]: The list of stored entries, or an empty list if the key
            does not exist or contains no data.

        Raises:
            Exception: If the Redis operation fails.
        """
        if not self.connection.exists(key):
            return []
        try:
            data = self.connection.json().get(key)
            return data if data else []
        except Exception as ex:
            raise ex

    def exists(self, key: str) -> bool:
        """
        Checks if a specific key exists in Redis.

        Parameters:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.connection.exists(key)

    # key helpers
    def _get_data_key(self, base_key: str) -> str:
        """Helper to generate the Redis key for the data hash."""
        return f"{base_key}:DATA"

    def _get_key_index_key(self, base_key: str) -> str:
        """Helper to generate the Redis key for the secondary index hash."""
        return f"{base_key}:INDEX:KEYS"

    def _get_time_index_key(self, base_key: str) -> str:
        """Helper to generate the Redis key for the time-sorted ZSET."""
        return f"{base_key}:INDEX:TIME"

    # optimized implementation
    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
        """
        Atomically stores an entry and updates secondary and time indices.

        Storage Structure:
        1. **Data Hash**: Stores `entry_id` -> `json_string` in `{base_key}:DATA`.
        2. **Key Index**: Stores `custom_key` -> `entry_id` in `{base_key}:INDEX:KEYS` (optional).
        3. **Time Index**: Stores `entry_id` with score `timestamp` in `{base_key}:INDEX:TIME`.

        Parameters:
            base_key (str): The base identifier for the collection.
            entry_id (str): Unique ID for the specific entry.
            entry (Dict): The data payload to store.
            custom_key (Optional[str]): A secondary lookup key (e.g., a tag).
            timestamp (float): The timestamp associated with the entry.

        Returns:
            bool: None (implicitly), raises exception on failure.

        Raises:
            Exception: If any Redis command fails.
        """
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
        """
        Retrieves a specific entry directly by its unique ID from the data hash.

        Parameters:
            base_key (str): The base identifier for the collection.
            entry_id (str): The unique ID of the entry.

        Returns:
            Optional[Dict]: The deserialized entry data, or None if not found.

        Raises:
            Exception: If the Redis operation fails.
        """
        try:
            result = self.connection.hget(self._get_data_key(base_key), entry_id)
            return json.loads(result) if result else None
        except Exception as ex:
            raise ex

    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
        """
        Retrieves an entry using the secondary custom key index.
        This performs two lookups: one to resolve the ID, and one to get the data.

        Parameters:
            base_key (str): The base identifier for the collection.
            custom_key (str): The secondary lookup key.

        Returns:
            Optional[Dict]: The entry data if found, None otherwise.

        Raises:
            Exception: If the Redis operation fails.
        """
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
        """
        Retrieves entries falling within a specific time range using the ZSET index.
        This is optimized to use `HMGET` for batch retrieval after identifying IDs.

        Parameters:
            base_key (str): The base identifier for the collection.
            start (float): The start timestamp (score).
            end (float): The end timestamp (score).

        Returns:
            List[Dict]: A list of deserialized entries found in the range.

        Raises:
            Exception: If the Redis operation fails.
        """
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
