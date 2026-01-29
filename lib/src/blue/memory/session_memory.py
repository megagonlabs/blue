import time
from typing import List, Dict, Any, Optional
from blue.memory.memory import Memory
from blue.utils import uuid_utils
from blue.memory.memory_store import MemoryStore


class SessionMemory(Memory):
    """
    Specialized Memory for Sessions.
    Delegates to the Store using a unique base_key per session.
    """

    def __init__(self, prefix: str, properties: Dict, store: MemoryStore = None):
        super().__init__(prefix, properties, store)

    def _get_session_memory_key(self, session_id: str) -> str:
        return self._get_scoped_key("SESSION", session_id)

    def store_session_memory(self, session_id: str, agent_id: str, data: Any, tags: List[str] = None, key: str = None) -> str:
        entry_id = f"memory_{uuid_utils.create_uuid()}_{agent_id}"
        timestamp = time.time()
        entry = {
            "id": entry_id,
            "agent_id": agent_id,
            "timestamp": timestamp,
            "data": data,
            "tags": tags or [],
            "key": key,  # Optional custom key for direct lookup
        }
        self._store_indexed_entry(base_key=self._get_session_memory_key(session_id), entry_id=entry_id, entry=entry, custom_key=key, timestamp=timestamp)
        return entry_id

    def retrieve_session_memory_by_id(self, session_id: str, id: str) -> Optional[Dict]:
        return self._get_entry_by_id(base_key=self._get_session_memory_key(session_id), entry_id=id)

    def retrieve_session_memory_by_key(self, session_id: str, key: str) -> Optional[Dict]:
        return self._get_entry_by_key_index(base_key=self._get_session_memory_key(session_id), custom_key=key)

    def retrieve_session_memory_by_time(self, session_id: str, start_time: float, end_time: float) -> List[Dict]:
        return self._get_entries_by_time_range(base_key=self._get_session_memory_key(session_id), start=start_time, end=end_time)

    def retrieve_session_memory_by_similarity(self, session_id: str, query_text: str, limit: int = 3) -> List[Dict]:
        # TODO: Implement vector search logic here
        return None
