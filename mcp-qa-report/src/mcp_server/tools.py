from mcp.server.fastmcp import FastMCP
from application.qa_runner import QARunner
from application.execution_context import ExecutionContext
from application.policies import FailFastPolicy
from infrastructure.checks.process_checks import MCPServerStartupCheck
from infrastructure.reporters.text_reporter import TextReporter
from infrastructure.checks.stdio_checks import STDIOIntegrityCheck
from infrastructure.checks.tool_checks import ToolsRegistrationCheck
from infrastructure.checks.tool_quality_checks import ToolDescriptionQualityCheck


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="qa_report",
        description="Run sanity and QA checks on an MCP project and return a structured checklist report."
    )
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
            STDIOIntegrityCheck(),
            ToolsRegistrationCheck(),
            ToolDescriptionQualityCheck(),
            # checks נוספים בהמשך
        ]

        results = QARunner(checks, FailFastPolicy()).run(ctx)

        return TextReporter().render(results)

