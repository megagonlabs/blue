from abc import ABC, abstractmethod
from typing import Dict, Any

class LogStore(ABC):
    """
    Abstract base class for pluggable structured log storage backends.

    Each backend (RedisLogStore, PostgresLogStore, S3LogStore, etc.)
    must implement the `write()` method.
    """

    @abstractmethod
    def write(self, record: Dict[str, Any]):
        """
        Persist a structured record.

        Args:
            record (dict): A structured event emitted by SearchableCustomLogger.

        Returns:
            Any backend-specific handle or ID for the written record.
        """
        pass
