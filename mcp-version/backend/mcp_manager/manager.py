from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_manager.config import MCP_SERVERS

import json

@dataclass
class MCPConnection:
    session: ClientSession
    stdio_cm: any
    session_cm: any

class MCPManager:
    def __init__(self):
        self.connections = {}

    async def startup(self):
        for server_name, server_config in MCP_SERVERS.items():
            print(f"Connecting to {server_name}...")

            server = StdioServerParameters(
                command = server_config["command"],
                args = server_config["args"]
            )

            stdio_cm = stdio_client(server)
            read, write = await stdio_cm.__aenter__()

            session_cm = ClientSession(read, write)
            session = await session_cm.__aenter__()

            await session.initialize()

            tools = await session.list_tools()

            print(f"{server_name} tools:")

            for tool in tools.tools:
                print("-", tool.name)

            self.connections[server_name] = MCPConnection(
                session=session,
                session_cm=session_cm,
                stdio_cm=stdio_cm
            )

            print(f"{server_name} connected successfully.")

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        connection = self.connections[server_name]

        session = connection.session

        result = await session.call_tool(
            tool_name,
            arguments
        ) 

        result_text = "".join(
            block.text
            for block in result.content
            if hasattr(block, "text")
        )

        if getattr(result, "isError", False):
            return {
                "status": "error",
                "error": result_text or "Unknown MCP execution error"
            }

        try:
            return json.loads(result_text)
        except (json.JSONDecodeError, TypeError):
            return result_text

    async def shutdown(self):
        for server_name, conn in self.connections.items():
            print(f"Disconnecting from {server_name}...")

            try:
                await conn.session_cm.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error closing session for {server_name}: {e}")
            finally:
                try:
                    await conn.stdio_cm.__aexit__(None, None, None)
                except Exception as e:
                    print(f"Error closing stdio for {server_name}: {e}")

        self.connections.clear()
        print("All MCP connections shut down successfully.")

mcp_manager = MCPManager()            