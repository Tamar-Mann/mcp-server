from application.execution_context import ExecutionContext
from infrastructure.checks.process_checks import MCPServerStartupCheck
from domain.models import CheckStatus

def test_startup_check_fails_on_invalid_command():
    ctx = ExecutionContext(
        project_path=".",
        command=["nonexistent_command"]
    )

    check = MCPServerStartupCheck()
    result = check.run(ctx)

    assert result.status == CheckStatus.FAIL

"""
אפשר להוסיף:

timeout → FAIL

stdout לא JSON → FAIL

JSON בלי jsonrpc → FAIL"""


"""def test_fails_when_no_command_provided():
    ctx = ExecutionContext(
        project_path=".",
        command=[],
    )

    check = MCPServerStartupCheck()
    result = check.run(ctx)

    assert result.status == CheckStatus.FAIL
    assert "No MCP command provided" in result.message"""
