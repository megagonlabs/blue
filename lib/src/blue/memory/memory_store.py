from abc import ABC, abstractmethod
from typing import List, Dict


class MemoryStore(ABC):
    """
    Abstract base class for pluggable structured memory storage backends.
    """

    @abstractmethod
    def initialize(self):
        """Initialize connections or structures."""
        pass

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
        """Check if a key exists."""
        pass
