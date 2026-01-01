from mcp.server.fastmcp import FastMCP
from application.qa_runner import QARunner
from application.execution_context import ExecutionContext
from application.policies import FailFastPolicy
from infrastructure.checks.process_checks import MCPServerStartupCheck
from infrastructure.reporters.text_reporter import TextReporter



def register(mcp: FastMCP) -> None:
    @mcp.tool(name="qa_report")
    def qa_check(
    project_path: str = ".",
    command: list[str] | None = None,
    ) -> str:
        ctx = ExecutionContext(
            project_path=project_path,
            command=command,
        )

        checks = [
            MCPServerStartupCheck(),
            # checks נוספים בהמשך
        ]

        results = QARunner(checks, FailFastPolicy()).run(ctx)

        return TextReporter().render(results)

