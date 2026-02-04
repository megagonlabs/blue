import time
from typing import List, Dict, Any, Optional
from blue.memories.memory import Memory
from blue.utils import uuid_utils
from blue.memories.memory_store import MemoryStore


class SessionMemory(Memory):
    """
    Specialized Memory management for individual Sessions.

    This class extends the base `Memory` class to provide scoped storage for session-specific
    data. It handles the generation of unique keys for each session and provides high-level
    methods for storing and retrieving memory entries (e.g., chat logs, state, context)
    associated with a specific session ID.

    Attributes:
        prefix (str): Inherited from `Memory`. The base prefix for keys.
        store (MemoryStore): Inherited from `Memory`. The underlying storage engine.
    """

    def __init__(self, prefix: str, properties: Dict, store: MemoryStore = None):
        """
        Initialize the SessionMemory instance.

        Parameters:
            prefix (str): The base prefix for all keys (e.g., 'PLATFORM').
            properties (Dict): Configuration properties passed to the underlying store.
            store (MemoryStore, optional): Explicit store instance. Defaults to None.
        """
        super().__init__(prefix, properties, store)

    def _get_session_memory_key(self, session_id: str) -> str:
        """
        Generates the scoped base key for a specific session.

        Pattern: `{prefix}:MEMORY:SESSION:{session_id}`

        Parameters:
            session_id (str): The unique identifier of the session.

        Returns:
            str: The fully namespaced key for the session.
        """
        return self._get_scoped_key("SESSION", session_id)

    def store_session_memory(self, session_id: str, agent_id: str, data: Any, tags: List[str] = None, key: str = None) -> str:
        """
        Stores a new memory entry for a given session.

        This method automatically:
        1. Generates a unique entry ID (combining UUID and Agent ID).
        2. Captures the current timestamp.
        3. Wraps the payload in a standard envelope (metadata + data).
        4. Indexes the entry by ID, time, and optionally a custom key.

        Parameters:
            session_id (str): The session to attach this memory to.
            agent_id (str): The ID of the agent creating this memory.
            data (Any): The actual content to store (e.g., a message object, state dict).
            tags (List[str], optional): specific tags for categorization. Defaults to None.
            key (str, optional): A custom unique key for direct O(1) retrieval later.
                (e.g., 'latest_summary'). Defaults to None.

        Returns:
            str: The unique ID generated for the stored memory entry.
        """
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
        """
        Retrieves a specific memory entry by its unique internal ID.

        Parameters:
            session_id (str): The session ID context.
            id (str): The unique entry ID (returned by `store_session_memory`).

        Returns:
            Optional[Dict]: The complete memory object if found, None otherwise.
        """
        return self._get_entry_by_id(base_key=self._get_session_memory_key(session_id), entry_id=id)

    def retrieve_session_memory_by_key(self, session_id: str, key: str) -> Optional[Dict]:
        """
        Retrieves a specific memory entry using a custom user-defined key.

        This is useful for fetching "singleton" memories like 'summary' or 'last_state'
        without knowing the generated UUID.

        Parameters:
            session_id (str): The session ID context.
            key (str): The custom key provided during storage.

        Returns:
            Optional[Dict]: The complete memory object if found, None otherwise.
        """
        return self._get_entry_by_key_index(base_key=self._get_session_memory_key(session_id), custom_key=key)

    def retrieve_session_memory_by_time(self, session_id: str, start_time: float, end_time: float) -> List[Dict]:
        """
        Retrieves all memory entries for a session within a specific time window.

        Parameters:
            session_id (str): The session ID context.
            start_time (float): The start timestamp (inclusive, Unix epoch).
            end_time (float): The end timestamp (inclusive, Unix epoch).

        Returns:
            List[Dict]: A list of memory objects sorted by time (depending on store implementation).
        """
        return self._get_entries_by_time_range(base_key=self._get_session_memory_key(session_id), start=start_time, end=end_time)

    def retrieve_session_memory_by_similarity(self, session_id: str, query_text: str, limit: int = 3) -> List[Dict]:
        """
        Retrieves memory entries based on semantic similarity to a query text.

        Note:
            This method is currently a placeholder and not yet implemented.

        Parameters:
            session_id (str): The session ID context.
            query_text (str): The text to compare against memory embeddings.
            limit (int, optional): The maximum number of results to return. Defaults to 3.

        Returns:
            List[Dict]: A list of most relevant memory objects (currently None).
        """
        # TODO: Implement vector search logic here
        return None
