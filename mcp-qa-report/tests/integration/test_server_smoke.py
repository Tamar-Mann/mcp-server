import pytest
from pathlib import Path

from infrastructure.runner_factory import RunnerFactory
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.errors import JsonRpcTimeoutError
import asyncio


@pytest.mark.integration
@pytest.mark.asyncio
async def test_server_starts_and_lists_tools():
    project_root = Path(__file__).resolve().parents[2]  
    cmd = detect_mcp_command(str(project_root))
    assert cmd is not None, "Could not detect MCP start command (check .vscode/mcp.json or pyproject scripts)"

    factory = RunnerFactory()
    async with factory.create(cmd, str(project_root), timeout_sec=10) as s:
        try:
            init = await s.client.initialize()
        except JsonRpcTimeoutError as e:
            pytest.fail(f"{e}\n\n--- stderr tail ---\n{s.runner.stderr_tail}")

        assert init and "result" in init, f"Bad init response: {init}\n\n--- stderr tail ---\n{s.runner.stderr_tail}"

        tools = await s.client.call("tools/list", request_id=2)
        assert tools and "result" in tools, f"Bad tools/list response: {tools}\n\n--- stderr tail ---\n{s.runner.stderr_tail}"
