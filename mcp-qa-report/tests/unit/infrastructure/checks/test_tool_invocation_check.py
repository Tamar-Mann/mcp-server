import pytest
from application.execution_context import ExecutionContext
from infrastructure.checks.invocation_checks import ToolInvocationCheck
from domain.models import CheckStatus

@pytest.mark.asyncio
async def test_invocation_warns_when_no_ping(ctx_factory, fake_session):
    # Setup: Server supports tools but specifically lacks the 'ping' health check tool
    fake_session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
    fake_session.client.call.side_effect = [
        {"jsonrpc": "2.0", "id": 20, "result": {"tools": [{"name": "qa_report", "inputSchema": {}, "description": "x"}]}},
        None # No second call expected
    ]
        
    ctx = ExecutionContext(project_path=".", command=["python"], runner_factory=ctx_factory)
    res = await ToolInvocationCheck().run(ctx)
    
    assert res.status == CheckStatus.WARN
    assert "No ping tool" in res.message

@pytest.mark.asyncio
async def test_invocation_passes_when_ping_exists_and_call_ok(ctx_factory, fake_session):
    # Setup: Server provides 'ping' tool and it responds with 'ok' when called
    fake_session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
    fake_session.client.call.side_effect = [
        {"jsonrpc": "2.0", "id": 20, "result": {"tools": [{"name": "ping", "inputSchema": {}, "description": "Health check"}]}},
        {"jsonrpc": "2.0", "id": 30, "result": {"content": [{"type": "text", "text": "ok"}]}},
    ]
        
    ctx = ExecutionContext(project_path=".", command=["python"], runner_factory=ctx_factory)
    res = await ToolInvocationCheck().run(ctx)
    
    assert res.status == CheckStatus.PASS