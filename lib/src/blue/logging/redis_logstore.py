import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from .logstore import LogStore
from blue.connection import PooledConnectionFactory

class RedisLogStore(LogStore):
    """
    Redis-backed structured event store for Blue logging.
    """

    NAMESPACE = "LOGS"

    DEFAULT_PROPERTIES = {
        "db.host": "localhost",
        "db.port": 6379,
        "platform.id": "default",
    }

    def __init__(self, properties: Optional[dict] = None, index_name="LOGS"):
        self.properties = dict(self.DEFAULT_PROPERTIES)
        if properties:
            self.properties.update(properties)

        self.index_name = index_name
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.redis = self.connection_factory.get_connection()

    # -----------------------------------------------------
    # Sanitization
    # -----------------------------------------------------
    def _sanitize(self, val: str) -> str:
        """Prevents Redis key clashes and search issues."""
        return val.replace(" ", "_").replace(":", "_").replace("/", "_")

    # -----------------------------------------------------
    # Namespace construction
    # -----------------------------------------------------
    def _context_to_namespace(self, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return "SYSTEM"

        parts = []
        for key in sorted(context.keys()):
            value = context[key]
            seg_key = key.upper()
            seg_val = self._sanitize(str(value))
            parts.append(f"{seg_key}:{seg_val}")

        return ":".join(parts)

    def _log_key(self, context=None):
        platform = self._sanitize(self.properties.get("platform.id", "default"))
        ctx = self._context_to_namespace(context)

        date_str = datetime.utcnow().strftime("%Y%m%d")
        uid = uuid.uuid4()

        return f"PLATFORM:{platform}:{self.NAMESPACE}:DATA:{ctx}:{date_str}:{uid}"

    # -----------------------------------------------------
    # Write operation
    # -----------------------------------------------------
    def write(self, record: dict, context: Optional[Dict[str, Any]] = None):
        record = dict(record)
        record["context"] = dict(context or {})

        key = self._log_key(context=context)

        try:
            self.redis.json().set(key, "$", record)
        except Exception as e:
            raise RuntimeError(f"Failed to store log record ({key}): {e}")

        return key
