from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class MemoryStore(ABC):
    """
    Abstract Base Class (interface) for memory storage backends.

    This interface defines the contract that all concrete storage implementations
    (e.g., `RedisMemoryStore`, `InMemoryStore`) must adhere to. It supports two primary
    data access patterns:
    1.  **List-based storage**: Appending items to a simple sequence.
    2.  **Indexed storage**: Storing items with support for lookups by unique ID,
        secondary custom keys, and time ranges.

    The `base_key` parameter used in many methods serves as the unique namespace
    or scope identifier (e.g., specific to a user session or agent).
    """

    @abstractmethod
    def initialize(self):
        """
        Initialize the storage backend.

        This method should handle setting up connections, creating necessary
        tables or data structures, and ensuring the store is ready for operations.
        """
        pass

    # list methods
    @abstractmethod
    def append_to_list(self, key: str, entry: Dict) -> bool:
        """
        Appends a dictionary entry to a sequential list stored at the given key.

        Parameters:
            key (str): The specific storage key for the list.
            entry (Dict): The data object to append.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def get_list(self, key: str) -> List[Dict]:
        """
        Retrieves the full list of entries stored at the given key.

        Parameters:
            key (str): The specific storage key to retrieve.

        Returns:
            List[Dict]: A list of all stored entries. Returns an empty list if
            the key does not exist.
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Checks if a specific key exists in the storage.

        Parameters:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        pass

    # indexed methods
    @abstractmethod
    def store_indexed_entry(self, base_key: str, entry_id: str, entry: Dict, custom_key: Optional[str], timestamp: float) -> bool:
        """
        Atomically stores an entry and updates all associated indices.

        Implementations should ensure that the data is retrievable by:
        1. Its `entry_id` (via `get_entry_by_id`).
        2. Its `custom_key` (via `get_entry_by_key_index`), if provided.
        3. Its `timestamp` (via `get_entries_by_time_range`).

        Parameters:
            base_key (str): The base namespace/scope identifier.
            entry_id (str): The unique ID for this specific entry.
            entry (Dict): The actual data payload to store.
            custom_key (Optional[str]): A secondary unique key for direct lookup
                (e.g., 'latest_summary').
            timestamp (float): The Unix timestamp associated with the entry.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def get_entry_by_id(self, base_key: str, entry_id: str) -> Optional[Dict]:
        """
        Retrieves a specific entry directly by its unique ID.

        Parameters:
            base_key (str): The base namespace/scope identifier.
            entry_id (str): The unique ID of the entry to retrieve.

        Returns:
            Optional[Dict]: The entry data if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_entry_by_key_index(self, base_key: str, custom_key: str) -> Optional[Dict]:
        """
        Retrieves a specific entry using a secondary custom key (index).

        Parameters:
            base_key (str): The base namespace/scope identifier.
            custom_key (str): The secondary lookup key used during storage.

        Returns:
            Optional[Dict]: The entry data if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_entries_by_time_range(self, base_key: str, start: float, end: float) -> List[Dict]:
        """
        Retrieves a list of entries falling within a specific time range.

        Parameters:
            base_key (str): The base namespace/scope identifier.
            start (float): The start timestamp (inclusive).
            end (float): The end timestamp (inclusive).

        Returns:
            List[Dict]: A list of entries found within the specified time window.
        """
        pass
