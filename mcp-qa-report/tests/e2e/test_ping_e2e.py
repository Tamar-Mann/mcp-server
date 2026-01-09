import pytest
from pathlib import Path
import asyncio

from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
from infrastructure.errors import JsonRpcTimeoutError


def _extract_text(resp: dict) -> str:
    if not resp:
        return ""
    if "error" in resp:
        return str(resp["error"])
    result = resp.get("result") or {}
    content = result.get("content") or []
    return "\n".join(
        item.get("text", "")
        for item in content
        if isinstance(item, dict) and item.get("type") == "text"
    )


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_ping_tool_returns_ok():
    project_root = Path(__file__).resolve().parents[2]  # mcp-qa-report

    cmd = detect_mcp_command(str(project_root))
    assert cmd is not None, "Could not detect MCP start command"

    factory = RunnerFactory()
    async with factory.create(cmd, str(project_root), timeout_sec=20) as s:
        try:
            init = await s.client.initialize()
        except JsonRpcTimeoutError as e:
            pytest.fail(f"{e}\n\n--- server stderr tail ---\n{s.runner.stderr_tail}")

        assert init and "result" in init, f"Bad init response: {init}\n\n--- server stderr tail ---\n{s.runner.stderr_tail}"

        try:
            resp = await s.client.call(
                "tools/call",
                request_id=50,
                params={"name": "ping", "arguments": {}},
            )
        except JsonRpcTimeoutError as e:
            pytest.fail(f"{e}\n\n--- server stderr tail ---\n{s.runner.stderr_tail}")

        text = _extract_text(resp).strip()
        assert text == "ok", f"Unexpected ping response: {text!r}\nraw={resp}"
