from mcp.server.fastmcp import FastMCP
import os

# Create an MCP server
mcp = FastMCP("ARGOS Filesystem")

@mcp.tool()
def list_files(path: str = ".") -> str:
    """List files in the specified directory."""
    try:
        return str(os.listdir(path))
    except Exception as e:
        return f"Error listing files: {e}"

@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    mcp.run()
