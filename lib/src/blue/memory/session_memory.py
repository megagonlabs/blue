import time
from typing import List, Dict, Any, Optional
from blue.memory.memory import Memory
from blue.utils import uuid_utils


class SessionMemory(Memory):
    """
    Specialized Memory for Sessions.
    Stores data under keys: ...:MEMORY:SESSION:{session_id}
    """

    def __init__(self, properties: Dict, prefix: str):
        super().__init__(properties, prefix)

    def _get_session_memory_key(self, session_id: str) -> str:
        return self._get_scoped_key("SESSION", session_id)

    def store_session_memory(self, session_id: str, agent_id: str, data: Any, tags: List[str] = None, key: str = None) -> str:
        redis_key = self._get_session_memory_key(session_id)
        entry_id = f"mem_{uuid_utils.create_uuid()}_{agent_id}"
        entry = {
            "id": entry_id,
            "agent_id": agent_id,
            "timestamp": time.time(),
            "data": data,
            "tags": tags or [],
            "key": key,  # Optional custom key for direct lookup
        }
        self._append_to_list(redis_key, entry)
        return entry_id

    def retrieve_session_memory_by_id(self, session_id: str, id: str) -> Optional[Dict]:
        redis_key = self._get_session_memory_key(session_id)
        memories = self._get_list(redis_key)
        for entry in reversed(memories):
            if entry.get("id") == id:
                return entry
        return None

    def retrieve_session_memory_by_key(self, session_id: str, key: str) -> Optional[Dict]:
        redis_key = self._get_session_memory_key(session_id)
        memories = self._get_list(redis_key)
        for entry in reversed(memories):
            if entry.get("key") == key:
                return entry
        return None

    def retrieve_session_memory_by_time(self, session_id: str, start_time: float, end_time: float) -> List[Dict]:
        redis_key = self._get_session_memory_key(session_id)
        memories = self._get_list(redis_key)
        results = []
        for entry in memories:
            timestamp = entry.get("timestamp", 0)
            if start_time <= timestamp <= end_time:
                results.append(entry)
        return results

    def retrieve_session_memory_by_similarity(self, session_id: str, query_text: str, limit: int = 3) -> List[Dict]:
        return None
