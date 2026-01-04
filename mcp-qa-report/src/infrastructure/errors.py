class MCPQAError(Exception):
    """Base error for MCP QA runner."""


class JsonRpcTimeoutError(MCPQAError):
    pass


class JsonRpcProtocolError(MCPQAError):
    pass


class MCPProcessError(MCPQAError):
    pass
