# src/mcp_server/server.py
from infrastructure.logging_config import configure_logging

configure_logging() 

from mcp.server.fastmcp import FastMCP
from mcp_server import tools



mcp = FastMCP("qa-report")
tools.register(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
