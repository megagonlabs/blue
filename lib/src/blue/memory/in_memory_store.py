from blue.memory.memory_store import MemoryStore
from typing import List, Dict


class InMemoryStore(MemoryStore):
    """
    In-Memory implementation using a Python dictionary.
    """

    def __init__(self):
        self._store = {}

    def initialize(self):
        pass

    def append_to_list(self, key: str, entry: Dict) -> bool:
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(entry)
        return True

    def get_list(self, key: str) -> List[Dict]:
        return self._store.get(key, [])

    def exists(self, key: str) -> bool:
        return key in self._store
