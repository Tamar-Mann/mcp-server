from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from infrastructure.process_runner import MCPProcessRunner
from infrastructure.jsonrpc_client import JsonRpcClient


@dataclass
class MCPClientSession:
    runner: MCPProcessRunner
    timeout_sec: int
    _client: Optional[JsonRpcClient] = None

    def __enter__(self) -> "MCPClientSession":

        self.runner.start()
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

    def __exit__(self, exc_type, exc, tb) -> None:
        
        try:
            self.runner.terminate()
        finally:
            if self._client is not None:
                self._client.close()
                self._client = None


class RunnerFactory:
    def create(self, command: list[str], project_path: str, timeout_sec: int) -> MCPClientSession:
        runner = MCPProcessRunner(command=command, project_path=project_path)
        return MCPClientSession(runner=runner, timeout_sec=timeout_sec)
