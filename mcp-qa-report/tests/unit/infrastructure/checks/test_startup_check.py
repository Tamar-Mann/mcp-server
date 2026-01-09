import pytest
from application.execution_context import ExecutionContext
from infrastructure.checks.process_checks import MCPServerStartupCheck
from domain.models import CheckStatus

@pytest.mark.asyncio
async def test_startup_check_fails_when_no_command_and_detect_none(monkeypatch, ctx_factory):
    monkeypatch.setattr("infrastructure.checks.process_checks.detect_mcp_command", lambda _: None)
    ctx = ExecutionContext(project_path=".", runner_factory=ctx_factory)
    res = await MCPServerStartupCheck().run(ctx)
    assert res.status == CheckStatus.FAIL

@pytest.mark.asyncio
async def test_startup_check_passes_on_initialize_result(ctx_factory, fake_session):
    fake_session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    
    ctx = ExecutionContext(
        project_path=".", 
        command=["python", "-m", "x"], 
        runner_factory=ctx_factory
    )
    res = await MCPServerStartupCheck().run(ctx)
    assert res.status == CheckStatus.PASS