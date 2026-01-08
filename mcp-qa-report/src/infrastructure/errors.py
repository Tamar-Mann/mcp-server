"""
Typed errors for MCP QA.

Provides a small exception hierarchy for process, protocol, and timeout failures
to keep error handling consistent across checks.
"""

class MCPQAError(Exception):
    """Base error for MCP QA runner."""


class JsonRpcTimeoutError(MCPQAError):
    pass


class JsonRpcProtocolError(MCPQAError):
    pass


class MCPProcessError(MCPQAError):
    pass
