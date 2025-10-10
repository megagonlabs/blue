###### Blue
from blue.operators.server import OperatorServer
from blue.tools.servers.mcp_server import MCPToolServer


#####
class MCPOperatorServer(MCPToolServer, OperatorServer):
    """MCP server for operators, inherits from MCPToolServer and OperatorServer."""

    def __init__(self, name, properties={}):
        """Initialize the MCPOperatorServer.

        Parameters:
            name: Name of the MCP operator server.
            properties: Properties for the server. Defaults to {}.
        """
        super().__init__(name, properties=properties)

    ##### operators
    def initialize_operators(self):
        """Initialize operators from MCP server."""
        super().initialize_tools()

    def add_operator(self, operator):
        """Add an operator to the MCP server.

        Parameters:
            operator: Operator object to be added.
        """
        super().add_tool(operator)

    def list_operators(self):
        """List available operators on the MCP server.

        Returns:
            List of available operators.
        """
        return super().list_tools(self)
