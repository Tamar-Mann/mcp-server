import pytest
from application.execution_context import ExecutionContext
from infrastructure.checks.tool_checks import ToolsRegistrationCheck
from domain.models import CheckStatus


@pytest.mark.asyncio
async def test_tools_registration_fails_on_invalid_schema(ctx_factory):
    # Setup: Mock a session that returns a tool with a missing 'inputSchema'
    async with ctx_factory.create(None, None, None) as session:
        session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        session.client.call.return_value = {
            "jsonrpc": "2.0", 
            "id": 2, 
            "result": {"tools": [{"name": "x"}]} # Missing inputSchema field
        }

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await ToolsRegistrationCheck().run(ctx)
    assert res.status == CheckStatus.FAIL


@pytest.mark.asyncio
async def test_tools_registration_passes_on_valid_tools(ctx_factory):
    # Setup: Mock a session that returns a valid tool definition
    async with ctx_factory.create(None, None, None) as session:
        session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        session.client.call.return_value = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "good enough"}]},
        }

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await ToolsRegistrationCheck().run(ctx)
    assert res.status == CheckStatus.PASS