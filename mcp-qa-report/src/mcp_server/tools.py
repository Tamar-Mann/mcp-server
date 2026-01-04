from infrastructure.reporters.report_writer import write_report_files, write_text_file
from mcp.server.fastmcp import FastMCP
from application.execution_context import ExecutionContext
from application.container import build_runner, build_reporter
from domain.ports import Reporter
from pathlib import Path


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="qa_report",
        description="Run sanity and QA checks on an MCP project and return a structured checklist report."
    )
    def qa_report(
        project_path: str = ".",
        command: list[str] | None = None,
        fail_fast: bool = True,
        output_path: str | None = None,
    ) -> str:
        ctx = ExecutionContext(project_path=project_path, command=command)

        runner = build_runner(fail_fast=fail_fast)
        results = runner.run(ctx)

        reporter: Reporter = build_reporter()
        text = reporter.render(results)

        if output_path is not None:
            output_path = output_path.strip()
            if output_path:
                try:
                    op = Path(output_path)

                    if str(output_path).endswith(("/", "\\")) or op.suffix == "":
                        r = write_report_files(
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

                    p = write_text_file(
                        project_path=project_path,
                        output_file=str(op),
                        text_content=text,
                    )
                    return f"Wrote report to: {p}"

                except Exception as e:
                    return f"Failed writing report to file: {e}\n\n{text}"
        return text


    @mcp.tool(name="ping", description="Health check tool. Returns ok.")
    def ping() -> str:
        return "ok"
