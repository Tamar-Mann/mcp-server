"""
Factory for MCP client sessions.

Creates MCPProcessRunner + JsonRpcClient as an async context-managed session,
ensuring processes and resources are cleaned up reliably on exit.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from infrastructure.process_runner import MCPProcessRunner
from infrastructure.jsonrpc_client import JsonRpcClient

@dataclass
class MCPClientSession:
    runner: MCPProcessRunner
    timeout_sec: int
    _client: Optional[JsonRpcClient] = None

    async def __aenter__(self) -> "MCPClientSession":
        await self.runner.start()
        self._client = JsonRpcClient(
            stdin=self.runner.stdin,
            stdout=self.runner.stdout,
            timeout_sec=self.timeout_sec,
        )
        return self

    @property
    def client(self) -> JsonRpcClient:
        assert self._client is not None, "Session not entered yet"
        return self._client

    # Ensures the subprocess and RPC client are properly terminated even if an error occurs
    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await self.runner.terminate()
        finally:
            if self._client is not None:
                await self._client.close()
                self._client = None


class RunnerFactory:
    @asynccontextmanager
    async def create(self, command: list[str], project_path: str, timeout_sec: int) -> AsyncGenerator[MCPClientSession, None]:
        runner = MCPProcessRunner(command=command, project_path=project_path)
        session = MCPClientSession(runner=runner, timeout_sec=timeout_sec)
        async with session:
            yield session
