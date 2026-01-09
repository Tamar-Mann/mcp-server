"""
MCP tool registrations.

Exposes `qa_report` (runs QA checks and returns a checklist report),
and a minimal `ping` tool for health-check / safe e2e invocation tests.
"""
import asyncio
from infrastructure.reporters.report_writer import write_report_files, write_text_file
from mcp.server.fastmcp import FastMCP
from application.execution_context import ExecutionContext
from application.container import build_runner, build_reporter
from domain.ports import Reporter
from pathlib import Path

def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="qa_report",
        description=(
        "Run protocol-level QA checks on a local MCP project.\n\n"
        "Note: Auto-detection for Python projects automatically uses 'uv run' "
        "to ensure environment isolation and correct dependency loading.\n\n"

        "Typical usage:\n"
        "- Self-check: run against the current project (project_path='.')\n"
        "- External check: validate another MCP project by providing project_path\n\n"

        "Inputs:\n"
        "- project_path: Path to the target project. Defaults to the server working directory.\n"
        "- command: Optional explicit start command for the target MCP server.\n"
        "  If omitted, the tool attempts best-effort auto-detection using common MCP config files.\n"
        "  Providing an explicit command is recommended when available.\n"
        "- fail_fast: Stop on first failure (default: true).\n"
        "- output_path: Optional file or directory path to write the report.\n"
        "  If a directory (or no file extension), writes 'qa_report.txt' inside it.\n"
        "  If a file path, writes exactly to that file.\n\n"

        "Output:\n"
        "- If output_path is omitted, returns the checklist report as text.\n"
        "- If output_path is provided, writes the report to disk and returns a short confirmation message.\n\n"

        "Notes:\n"
        "- In environments where auto-detection is not possible (e.g. Codex sandboxes), an explicit command may be required.\n"
        "- Invalid output paths do not abort execution; the report is still returned inline."
        )
    )
    async def qa_report(
        project_path: str = ".",
        command: list[str] | None = None,
        fail_fast: bool = True,
        output_path: str | None = None,
    ) -> str:
        ctx = ExecutionContext(project_path=project_path, command=command)

        runner = build_runner(fail_fast=fail_fast)
        results = await runner.run(ctx)

        reporter: Reporter = build_reporter()
        text = reporter.render(results)

        if output_path is not None:
            output_path = output_path.strip()
            if output_path:
                try:
                    op = Path(output_path)

                    if op.is_dir() or str(output_path).endswith(("/", "\\")) or op.suffix == "":
                        r = await write_report_files(
                            project_path=project_path,
                            output_dir=str(op),
                            base_name="qa_report",
                            include_timestamp=False,   
                            write_text=True,
                            write_json=False,
                            text_content=text,
                            json_content="",
                        )
                        return f"Wrote report to: {r.text_path}"

                    p = await write_text_file(
                        project_path=project_path,
                        output_file=str(op),
                        text_content=text,
                    )
                    return f"Wrote report to: {p}"

                except Exception as e:
                    return f"Failed writing report to file: {e}\n\nReport:\n{text}"
        return text

    @mcp.tool(name="ping", description="Health check tool. Returns ok.")
    async def ping() -> str:
        return "ok"
