import pytest
from application.execution_context import ExecutionContext
from infrastructure.checks.tool_quality_checks import ToolDescriptionQualityCheck
from domain.models import CheckStatus


@pytest.mark.asyncio
async def test_tool_description_quality_warns_on_missing_desc(ctx_factory):
    # Test scenario: Tool exists but description is empty or just whitespace
    async with ctx_factory.create(None, None, None) as session:
        session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        session.client.call.return_value = {
            "jsonrpc": "2.0",
            "id": 10,
            "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "  "}]},
        }
        
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await ToolDescriptionQualityCheck().run(ctx)
    assert res.status == CheckStatus.WARN
    assert "Tools missing description" in res.message


@pytest.mark.asyncio
async def test_tool_description_quality_passes_when_all_have_desc(ctx_factory):
    # Test scenario: Tool has a valid, non-empty description
    async with ctx_factory.create(None, None, None) as session:
        session.client.initialize.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        session.client.call.return_value = {
            "jsonrpc": "2.0",
            "id": 10,
            "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "Nice description"}]},
        }
        
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await ToolDescriptionQualityCheck().run(ctx)
    assert res.status == CheckStatus.PASS