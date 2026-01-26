from blue.tools.clients.blue.memory_tools import create_memory_tools
from blue.memory.session_memory import SessionMemory
from blue.properties import PROPERTIES

session_memory = SessionMemory(properties=PROPERTIES, prefix=f"PLATFORM:{PROPERTIES.get('platform.name', 'default')}")
memory_tools_dict = create_memory_tools(session_memory)
tools_dict = {**memory_tools_dict}
