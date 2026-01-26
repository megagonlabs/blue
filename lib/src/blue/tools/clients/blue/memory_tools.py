from blue.tools.tool import Tool
from typing import List, Any, Dict
import time


def create_memory_tools(session_memory) -> Dict[str, Tool]:
    memory_tools_dict = {}

    def store_memory(data: Any, context: dict, tags: List[str] = None) -> str:
        """
        Stores information into the shared session memory.

        Parameters:
            data: The content to store.
            context: The execution context.
            tags: Optional tags.
        """
        session_id = context.get('session_id')
        agent_id = context.get('agent_id')
        if not session_id:
            raise ValueError("No session context.")
        if not agent_id:
            raise ValueError("No agent context.")
        return session_memory.store_memory(session_id=session_id, agent_id=agent_id, data=data, tags=tags)

    store_memory_tool = Tool(
        "store_memory", store_memory, description="Store information in session memory.", validator=lambda params: 'data' in params, explainer=lambda output, params: {"memory_id": output}
    )
    store_memory_tool.set_parameter_required('context', True)
    store_memory_tool.set_parameter_hidden('context', True)
    memory_tools_dict["store_memory"] = store_memory_tool

    def retrieve_memory_by_key(key: str, context: dict) -> Dict:
        """
        Retrieves a memory entry by key.

        Parameters:
            key: The unique key.
            context: The execution context.
        """
        session_id = context.get('session_id')
        if not session_id:
            raise ValueError("No session context.")
        result = session_memory.retrieve_memory_by_key(session_id, key)
        return result if result else None

    retrieve_by_key_tool = Tool("retrieve_memory_by_key", retrieve_memory_by_key, description="Fast memory retrieval by key.", validator=lambda params: 'key' in params)
    retrieve_by_key_tool.set_parameter_required('context', True)
    retrieve_by_key_tool.set_parameter_hidden('context', True)
    memory_tools_dict["retrieve_memory_by_key"] = retrieve_by_key_tool

    def retrieve_memory_by_time(minutes_ago: int, context: dict) -> List[Dict]:
        """
        Retrieves memories stored within the last N minutes (Chronological Recall).

        Parameters:
            minutes_ago: How many minutes back to search.
            context: The execution context.
        """
        session_id = context.get('session_id')
        if not session_id:
            raise ValueError("No session context.")
        end_time = time.time()
        start_time = end_time - (minutes_ago * 60)
        return session_memory.retrieve_memory_by_time(session_id, start_time, end_time)

    retrieve_by_time_tool = Tool(
        "retrieve_memory_by_time",
        retrieve_memory_by_time,
        description="Recall chronological events or memories from the last X minutes.",
        validator=lambda params: 'minutes_ago' in params and isinstance(params['minutes_ago'], int),
    )
    retrieve_by_time_tool.set_parameter_required('context', True)
    retrieve_by_time_tool.set_parameter_hidden('context', True)
    memory_tools_dict["retrieve_memory_by_time"] = retrieve_by_time_tool

    def retrieve_memory_by_similarity(query: str, context: dict) -> List[Dict]:
        """
        Retrieves memories based on similarity.

        Parameters:
            query: The search query.
            context: The execution context.
        """
        session_id = context.get('session_id')
        if not session_id:
            raise ValueError("No session context.")
        return session_memory.retrieve_memory_by_similarity(session_id, query)

    retrieve_by_similarity_tool = Tool("retrieve_memory_by_similarity", retrieve_memory_by_similarity, description="Semantic search for memories.", validator=lambda params: 'query' in params)
    retrieve_by_similarity_tool.set_parameter_required('context', True)
    retrieve_by_similarity_tool.set_parameter_hidden('context', True)
    memory_tools_dict["retrieve_memory_by_similarity"] = retrieve_by_similarity_tool
    return memory_tools_dict
