from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class MemoryStore(ABC):
    """
    Abstract interface for memory storage.
    The 'base_key' represents the unique identifier for the memory scope (e.g., a specific session).
    Supports both list storage and optimized indexed storage.
    """

    @abstractmethod
    def initialize(self):
        """Initialize connections or structures."""
        pass

    # list methods
    @abstractmethod
    def append_to_list(self, key: str, entry: Dict) -> bool:
        """Append an entry to a list at the given key."""
        pass

    @abstractmethod
    def get_list(self, key: str) -> List[Dict]:
        """Retrieve the full list from the given key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    # indexed methods
    @abstractmethod
    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
        """
        Atomically stores data and updates indices for the given base_key.
        """
        pass

    @abstractmethod
    def get_entry_by_id(self, base_key: str, entry_id: str) -> Optional[Dict]:
        """Direct retrieval by ID."""
        pass

    @abstractmethod
    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
        """Retrieval via secondary index (custom key)."""
        pass

    @abstractmethod
    def get_entries_by_time_range(self, base_key: str, start: float, end: float) -> List[Dict]:
        """Retrieval via time range index."""
        pass
