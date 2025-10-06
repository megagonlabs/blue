###### Blue
from blue.operators.server import OperatorServer
from blue.tools.servers.mcp_server import MCPToolServer


#####
class MCPOperatorServer(MCPToolServer, OperatorServer):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ##### operators
    def initialize_operators(self):
        super().initialize_tools()

    def add_operator(self, operator):
        super().add_tool(operator)

    def list_operators(self):
        return super().list_tools(self)
