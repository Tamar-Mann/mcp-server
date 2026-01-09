import json
from sys import stdin
import pytest
from unittest.mock import AsyncMock, MagicMock

from infrastructure.jsonrpc_client import JsonRpcClient
from infrastructure.errors import JsonRpcTimeoutError, JsonRpcProtocolError


class ExplodingStreamWriter:
    """Simulates a stream writer that fails during write operations."""
    def write(self, _): # Removed 'async'
        raise OSError("nope")

    async def drain(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass


@pytest.mark.asyncio
async def test_initialize_success_reads_matching_id():
    # Setup: Return a valid JSON-RPC response with matching ID 1
    stdout = AsyncMock()
    stdout.readline = AsyncMock(side_effect=[
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}).encode("utf-8") + b"\n"
    ])
    stdin = AsyncMock()
    stdin.write = MagicMock()  
    stdin.close = MagicMock() 
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp = await c.initialize()
        assert resp["result"]["ok"] is True
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_initialize_collects_noise_for_non_json_lines():
    # Setup: Mix plain text noise and notifications before the actual response
    lines = [
        b"HELLO THERE\n",
        json.dumps({"jsonrpc": "2.0", "method": "notifications/message", "params": {"x": 1}}).encode("utf-8") + b"\n",
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}).encode("utf-8") + b"\n",
        b"",
    ]
    stdout = AsyncMock()
    stdout.readline = AsyncMock(side_effect=lines)
    stdin = AsyncMock()
    stdin.write = MagicMock()  
    stdin.close = MagicMock() 
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp, noise = await c.initialize_collect_noise()
        assert resp["result"]["ok"] is True
        assert noise and noise[0] == "HELLO THERE"
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_call_ignores_other_ids_and_waits_for_expected():
    # Setup: Ensure the client filters out messages with IDs that don't match the request
    lines = [
        json.dumps({"jsonrpc": "2.0", "id": 999, "result": {"no": "this"}}).encode("utf-8") + b"\n",
        json.dumps({"jsonrpc": "2.0", "id": 20, "result": {"tools": []}}).encode("utf-8") + b"\n",
        b"",
    ]
    stdout = AsyncMock()
    stdout.readline = AsyncMock(side_effect=lines)
    stdin = AsyncMock()
    stdin.write = MagicMock()  
    stdin.close = MagicMock()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp = await c.call("tools/list", request_id=20)
        assert resp["result"]["tools"] == []
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_timeout_raises():
    # Setup: Simulate a timeout by reaching EOF without receiving a response
    stdout = AsyncMock()
    stdout.readline = AsyncMock(side_effect=[b""])  # EOF immediately
    stdin = AsyncMock()
    stdin.write = MagicMock()  
    stdin.close = MagicMock()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=0.2)
    try:
        with pytest.raises(JsonRpcTimeoutError):
            await c.initialize()
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_protocol_error_on_write_failure():
    stdout = AsyncMock()
    # No need to mock readline here, the crash happens on write
    
    stdin = ExplodingStreamWriter()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=0.2)
    
    try:
        # Now this will catch the JsonRpcProtocolError triggered by the OSError
        with pytest.raises(JsonRpcProtocolError):
            await c.initialize()
    finally:
        await c.close()