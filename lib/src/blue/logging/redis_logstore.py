import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

from .logstore import LogStore
from blue.connection import PooledConnectionFactory

from typing import List

from redis.commands.search.field import TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


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

        # create RediSearch index if not exists
        self._ensure_index()

    # -----------------------------------------------------
    # Create RediSearch index
    # -----------------------------------------------------
    def _ensure_index(self):
        """Create FT index for JSON logs if it does not already exist."""
        try:
            self.redis.ft(self.index_name).info()
            return  # index exists
        except Exception:
            pass

        platform_prefix = self._sanitize(self.properties["platform.id"])
        key_prefix = f"PLATFORM:{platform_prefix}:LOGS:DATA:"

        schema = [
            # Core text fields
            TextField("$.action", as_name="action"),
            TextField("$.detail", as_name="detail"),
            TextField("$.message", as_name="message"),
            TextField("$.question", as_name="question"),

            # Context filters
            TagField("$.context.session",   as_name="session"),
            TagField("$.context.agent",     as_name="agent"),
            TagField("$.context.worker",    as_name="worker"),
            TagField("$.context.plan",      as_name="plan"),
            TagField("$.context.operator",  as_name="operator"),

            # Catch-all semantic search blob
            TextField("$._blob", as_name="blob"),
        ]

        definition = IndexDefinition(
            index_type=IndexType.JSON,
            prefix=[key_prefix]
        )

        self.redis.ft(self.index_name).create_index(schema, definition=definition)
        #print(f"Created RediSearch index {self.index_name}")
    
    # -----------------------------------------------------
    # Sanitization
    # -----------------------------------------------------
    def _sanitize(self, val: str) -> str:
        """Prevents Redis key clashes and search issues."""
        return (
            val.replace(" ", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace("-", "_")      
        )


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
        """
        Write structured log record to RedisJSON and include `_blob`
        for full-text search.
        """
        record = dict(record)
        record["context"] = dict(context or {})

        # catch-all full-text blob for search
        record["_blob"] = json.dumps(record, ensure_ascii=False)

        key = self._log_key(context=context)

        try:
            self.redis.json().set(key, "$", record)
        except Exception as e:
            raise RuntimeError(f"Failed to store log record ({key}): {e}")

        return key

class LogSearchClient:
    DEFAULT_PROPERTIES = {
        "db.host": "localhost",
        "db.port": 6379,
        "platform.id": "default",
    }

    def __init__(
        self,
        properties: Optional[dict] = None,
        index_name: str = "LOGS",
    ):
        self.properties = dict(self.DEFAULT_PROPERTIES)
        if properties:
            self.properties.update(properties)

        self.index = index_name
        self.connection_factory = PooledConnectionFactory(
            properties=self.properties
        )
        self.redis = self.connection_factory.get_connection()


    # ---- Simple semantic helpers ----

    def by_action(self, action, **kwargs):
        return self.search(f"@action:{action}", **kwargs)

    def by_session(self, session_id, **kwargs):
        return self.search(f"@session:{{{session_id}}}", **kwargs)

    def by_agent(self, agent_prefix, **kwargs):
        return self.search(f"@agent:{{{agent_prefix}*}}", **kwargs)

    def text(self, keyword, **kwargs):
        return self.search(keyword, **kwargs)

    def recent(self, limit=20):
        return self.search("*", limit=limit)

    
    def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        return_fields: Optional[List[str]] = None,
        sort_by: Optional[str] = None,
        ascending: bool = False,
    ) -> List[Dict]:
        """
        Generic FT.SEARCH wrapper
        """
        args = [self.index, query]

        if sort_by:
            args += ["SORTBY", sort_by, "ASC" if ascending else "DESC"]

        if return_fields:
            args += ["RETURN", len(return_fields), *return_fields]

        args += ["LIMIT", offset, limit]

        raw = self.redis.execute_command("FT.SEARCH", *args)

        # raw format: [count, key1, doc1, key2, doc2, ...]
        results = []
        for i in range(1, len(raw), 2):
            doc = raw[i + 1]
            results.append(doc)

        return results


