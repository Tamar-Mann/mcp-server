"""
Minimal JSON-RPC 2.0 client for MCP over stdio.

Writes requests to stdin, reads stdout asynchronously to avoid blocking,
filters responses by expected id, and raises JsonRpcTimeoutError on timeout.
Supports collecting pre-initialize noise for STDIO integrity checks.
"""
import json
import asyncio
from typing import Optional

from infrastructure.errors import JsonRpcTimeoutError, JsonRpcProtocolError

class JsonRpcClient:
    """Async JSON-RPC client over stdio with request-id matching and timeouts."""
    def __init__(self, stdin: asyncio.StreamWriter, stdout: asyncio.StreamReader, timeout_sec: int):
        self._stdin = stdin
        self._stdout = stdout
        self._timeout = timeout_sec
        self._closed = False

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self._stdin is not None:
                self._stdin.close()
                await self._stdin.wait_closed()
        except Exception:
            pass

    async def initialize(self) -> dict | None:
        data, _ = await self._request_with_optional_noise(self._init_msg(), expected_id=1, collect_noise=False)
        return data

    async def initialize_collect_noise(self) -> tuple[dict | None, list[str]]:
        return await self._request_with_optional_noise(self._init_msg(), expected_id=1, collect_noise=True)

    async def call(self, method: str, request_id: int, params: dict | None = None) -> dict | None:
        msg = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        data, _ = await self._request_with_optional_noise(msg, expected_id=request_id, collect_noise=False)
        return data

    def _init_msg(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "qa-check", "version": "0.1.0"},
            },
        }

    async def _write_json(self, msg: dict) -> None:
        try:
            self._stdin.write(json.dumps(msg).encode("utf-8") + b"\n")
            await self._stdin.drain()
        except Exception as e:
            raise JsonRpcProtocolError(f"Failed writing JSON-RPC request: {e}") from e

    async def _request_with_optional_noise(
        self,
        msg: dict,
        expected_id: int,
        collect_noise: bool,
    ) -> tuple[dict | None, list[str]]:
        await self._write_json(msg)

        noise: list[str] = []

        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    # 1. Await the bytes FIRST. 
                    # This ensures the coroutine is finished before we touch the data.
                    line_bytes = await self._stdout.readline()
                    
                    if not line_bytes:
                        raise JsonRpcTimeoutError(f"EOF reached before response id={expected_id}")

                    # 2. Decode bytes to string separately
                    line_str = line_bytes.decode("utf-8", errors="replace")
                    
                    # 3. Strip whitespace from the string
                    s = line_str.strip()
                    
                    if not s:
                        continue

                    try:
                        data = json.loads(s)
                    except json.JSONDecodeError:
                        if collect_noise:
                            noise.append(s)
                        continue
                        
                    # Accept only the response that matches our request ID
                    if data.get("jsonrpc") == "2.0" and data.get("id") == expected_id:
                        if "result" in data or "error" in data:
                            return data, noise

        except asyncio.TimeoutError:
            raise JsonRpcTimeoutError(f"Timeout waiting for JSON-RPC response id={expected_id}")