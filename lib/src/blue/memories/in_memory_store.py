from blue.memories.memory_store import MemoryStore
from typing import List, Dict

from typing import List, Dict, Optional, Any, Tuple
from blue.memories.memory_store import MemoryStore


class InMemoryStore(MemoryStore):
    """
    In-memory implementation of the MemoryStore interface using standard Python dictionaries.

    This class serves as a volatile storage backend, primarily useful for testing,
    development, or non-persistent runtime memory. It mimics the structure of the
    `RedisMemoryStore` by separating data storage from indexing:

    - **Data Storage**: Uses a dictionary at `{base_key}:DATA` to map entry IDs to data.
    - **Key Index**: Uses a dictionary at `{base_key}:INDEX:KEYS` to map custom keys to entry IDs.
    - **Time Index**: Uses a list of tuples `(timestamp, entry_id)` at `{base_key}:INDEX:TIME`,
      sorted by timestamp, to facilitate range queries.

    Attributes:
        _store (Dict): The internal dictionary acting as the database.
    """

    def __init__(self):
        """
        Initialize the InMemoryStore with an empty storage dictionary.
        """
        self._store = {}

    def initialize(self):
        """
        No-op initialization for in-memory storage.
        """
        pass

    # key helpers
    def _get_data_key(self, base_key: str) -> str:
        """Helper to generate the internal key for the data dictionary."""
        return f"{base_key}:DATA"

    def _get_key_index_key(self, base_key: str) -> str:
        """Helper to generate the internal key for the secondary index dictionary."""
        return f"{base_key}:INDEX:KEYS"

    def _get_time_index_key(self, base_key: str) -> str:
        """Helper to generate the internal key for the time-sorted list."""
        return f"{base_key}:INDEX:TIME"

    def append_to_list(self, base_key: str, entry: Dict) -> bool:
        """
        Appends a dictionary entry to a list stored at the given key.

        Parameters:
            base_key (str): The storage key.
            entry (Dict): The data to append.

        Returns:
            bool: Always returns None (implicitly), mimicking the void return of a procedure.
        """
        if base_key not in self._store:
            self._store[base_key] = []
        if not isinstance(self._store[base_key], list):
            self._store[base_key] = []
        self._store[base_key].append(entry)

    def get_list(self, base_key: str) -> List[Dict]:
        """
        Retrieves the full list of entries stored at the given key.

        Parameters:
            base_key (str): The storage key.

        Returns:
            List[Dict]: The stored list, or an empty list if the key is missing or invalid.
        """
        result = self._store.get(base_key, [])
        return result if isinstance(result, list) else []

    def exists(self, base_key: str) -> bool:
        """
        Checks if the base key exists in the internal store.

        Parameters:
            base_key (str): The key to check.

        Returns:
            bool: True if key is present, False otherwise.
        """
        return base_key in self._store

    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
        """
        Atomically stores data and updates in-memory indices.

        1. **Data**: Stored in a nested dict under `{base_key}:DATA`.
        2. **Key Index**: Mapped in a nested dict under `{base_key}:INDEX:KEYS`.
        3. **Time Index**: Appended as `(timestamp, id)` to a list under `{base_key}:INDEX:TIME`
           and re-sorted.

        Parameters:
            base_key (str): The scope identifier.
            entry_id (str): Unique ID for the entry.
            entry (Dict): The data payload.
            custom_key (Optional[str]): Secondary lookup key.
            timestamp (float): The timestamp for sorting.

        Returns:
            bool: None (implicitly).
        """
        # store data
        data_key = self._get_data_key(base_key)
        if data_key not in self._store:
            self._store[data_key] = {}
        self._store[data_key][entry_id] = entry
        # update key index
        if custom_key:
            index_key = self._get_key_index_key(base_key)
            if index_key not in self._store:
                self._store[index_key] = {}
            self._store[index_key][custom_key] = entry_id
        # update time index
        time_key = self._get_time_index_key(base_key)
        if time_key not in self._store:
            self._store[time_key] = []
        # append tuple: (timestamp, id)
        self._store[time_key].append((timestamp, entry_id))
        # sort by timestamp
        self._store[time_key].sort(key=lambda x: x[0])

    def get_entry_by_id(self, base_key: str, entry_id: str) -> Optional[Dict]:
        """
        Retrieves an entry directly from the data dictionary.

        Parameters:
            base_key (str): The scope identifier.
            entry_id (str): The unique entry ID.

        Returns:
            Optional[Dict]: The entry data if found, None otherwise.
        """
        data_key = self._get_data_key(base_key)
        data_hash = self._store.get(data_key)
        if data_hash and isinstance(data_hash, dict):
            return data_hash.get(entry_id)
        return None

    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
        """
        Retrieves an entry by looking up the ID in the key index, then fetching the data.

        Parameters:
            base_key (str): The scope identifier.
            custom_key (str): The secondary lookup key.

        Returns:
            Optional[Dict]: The entry data if found, None otherwise.
        """
        # get ID from index
        index_key = self._get_key_index_key(base_key)
        index_hash = self._store.get(index_key)
        if not index_hash or not isinstance(index_hash, dict):
            return None
        entry_id = index_hash.get(custom_key)
        if not entry_id:
            return None
        # get data using ID
        return self.get_entry_by_id(base_key, entry_id)

    def get_entries_by_time_range(self, base_key: str, start: float, end: float) -> List[Dict]:
        """
        Retrieves entries within a time range by filtering the sorted time index list.

        Parameters:
            base_key (str): The scope identifier.
            start (float): Start timestamp (inclusive).
            end (float): End timestamp (inclusive).

        Returns:
            List[Dict]: A list of matching entries.
        """
        # get IDs from time index
        time_key = self._get_time_index_key(base_key)
        time_list = self._store.get(time_key, [])
        if not time_list or not isinstance(time_list, list):
            return []
        # filter tuples where start <= timestamp <= end
        entry_ids = [eid for ts, eid in time_list if start <= ts <= end]
        if not entry_ids:
            return []
        # batch get data
        results = []
        for eid in entry_ids:
            entry = self.get_entry_by_id(base_key, eid)
            if entry:
                results.append(entry)
        return results
