from blue.memory.memory_store import MemoryStore
from typing import List, Dict

from typing import List, Dict, Optional, Any, Tuple
from blue.memory.memory_store import MemoryStore


class InMemoryStore(MemoryStore):
    """
    In-memory implementation using Python dictionaries.
    """

    def __init__(self):
        self._store = {}

    def initialize(self):
        pass

    # --- Internal Key Helpers (Consistent with Redis logic) ---
    def _get_data_key(self, base_key: str) -> str:
        return f"{base_key}:DATA"

    def _get_key_index_key(self, base_key: str) -> str:
        return f"{base_key}:INDEX:KEYS"

    def _get_time_index_key(self, base_key: str) -> str:
        return f"{base_key}:INDEX:TIME"

    def append_to_list(self, base_key: str, entry: Dict) -> bool:
        if base_key not in self._store:
            self._store[base_key] = []
        if not isinstance(self._store[base_key], list):
            self._store[base_key] = []
        self._store[base_key].append(entry)

    def get_list(self, base_key: str) -> List[Dict]:
        result = self._store.get(base_key, [])
        return result if isinstance(result, list) else []

    def exists(self, base_key: str) -> bool:
        return base_key in self._store

    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
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
        data_key = self._get_data_key(base_key)
        data_hash = self._store.get(data_key)
        if data_hash and isinstance(data_hash, dict):
            return data_hash.get(entry_id)
        return None

    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
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
