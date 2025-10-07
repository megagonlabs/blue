# Tools

Blue supports tools - functions that can be called by agents. Tool use is Tools can be local functions, ray-based functions that can execute remotely on Ray clusters, or MCP-based tools that can be executed through MCP interface.

Below we will first, describe how to develop and use tools in agents. Then, we will go through an example development of MCP-based tool server. Finally, we will talk about tool registry and go through basic tool registry functions and show how tools can be used with an agent. For how to use tools with OpenAI agent refer to its [documentation](agents/openai). 

## Tool 

[`Tool`](lib/src/blue/tools/tool.py) is a base class that can either be used or extended depending on the need. Essentially, it defines the tool along with metadata such as name, description and properties, along with functions to execute, validate, and explain: `function`, `validator`, and `explainer` as callable functions.

As part of initializtion, signature of the function is extracted through `_extract_signature` function and saved as a property: `signature`. Signature, as a whole, individual parameters, and return as well as parameter metadata such as name, descriptions, and type can be get and set through functions such as `get_signature`, `get_parameters`, `get_parameter`, `get_parameter_type`, `is_parameter_required`, `get_returns`, etc. Please refer to the API documents for details.

Below is an example tool:

```
from typing import List

###### Blue
from blue.tools.tool import Tool

###############
### Local Tools Registry
tools_dict = {}

### add
def add(numbers: List[int]) -> int:
    result = 0
    for number in numbers:
        result += number
    return result


add_tool = Tool(
    "add",
    add,
    description="adds numbers and returns the addition as a result",
    validator=lambda params: 'numbers' in params and type(params['numbers']) == list and all([type(number) in [int, float] for number in params['numbers']]),
    explainer=lambda output, params: {"output": output, "params": params},
)
```


## Tool Servers

As explained before there are three types of tool servers, each come with different pros and cons for different use cases. Local tools execute locally in the current run time and as such they are as responsive as any other function. Ray based tool execute on a ray cluster, as such they offer scalability at the expense of remote execution and lower response time per call. MCP based tools execute over http streaming interface. Based on MCP standard they offer advantages in terms of integration. Any number of MCP servers can be registered in the tool registry.

### Local Tool Server

Once a tool is developed as described above it can be added to the local server. A very simple way to define a local tool server is extend `LocalToolClient` and keep a dictionary of tools, e.g.:
```
tools_dict = {}
tools_dict["add"] = add_tool
```
and create a local tools client, as below:
```
LocalToolClient(server, tools=tools_dict, properties=properties)
```

### Ray Tool Server

Ray tool development is no different than local tools development, except that `RayToolClient` should be used instead.

### MCP-based Tool Servers

MCP-based tool servers operate in a similar fashion except that they use MCP APIs to add tools, get list of tools, etc. Unlike local and ray based tools which only have a client (e.g. `LocalToolClient`) MCP based tools have a `MCPToolClient` and a server `MCPToolServer` as they are hosted externally.

Once deployed and running you can register your tool server using blue web interface, adding details such as connection properties, including `host`, `protocol` (should be `"mcp"`) `subprotocol` (e.g. `http` or `https`). See example MCP servers that come with blue installer.

### Developing your MCP Tool Server

`blue-examples` repo contains an example MCP server development. See `tools/basic_calculator` in that repo for more details. 

## Tool Registry

To interface your agent with the tool registry, in your agent code you need to create an instance of tool registry. Once you have an instance, you can query tool servers, tools on a server, execute tools, etc.

Below is an example:
```
from blue.tools.registry import ToolRegistry

platform_id = "default"
tool_registry_id = "default"

prefix = 'PLATFORM:' + platform_id
registry = ToolRegistry(id=tool_registry_id, prefix=prefix)

# get list of servers
tool_servers = registry.get_servers()

# get list of tools on a server
tools = registry.get_server_tools("blue_local")

# search tools
registry.search_records("add two numbers", approximate=True, type="tool")

# get instance of a tool
tool = get_server_tool("blue_local", "add")

# execute tool
kwargs = {"numbers": [1, 2]})
registry.execute_tool("add", "blue_local", None, kwargs)
```

Tool support is provided by default for OpenAI. See its [documentation](agents/openai) for more details.

