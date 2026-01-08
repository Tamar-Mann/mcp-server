from domain.models import CheckResult, CheckStatus
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
import logging

log = logging.getLogger(__name__)

class ToolDescriptionQualityCheck:
    """
    Evaluates the quality of tool descriptions exposed by the MCP server.

    Tools with missing or very short descriptions are reported as WARN,
    as poor metadata reduces usability for LLM-based agents.
    """
    name = "Tool description quality"

    def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(self.name, CheckStatus.FAIL, "Cannot determine MCP start command")

        factory = ctx.runner_factory or RunnerFactory()

        try:
            with factory.create(command, ctx.project_path, ctx.timeout_sec) as s:
                init = s.client.initialize()
                if not init or "result" not in init:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"Server did not respond to initialize{extra}")

                response = s.client.call("tools/list", request_id=10)
                if not response or "result" not in response:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"tools/list returned no result{extra}")

                tools = response["result"].get("tools", [])
                if not tools:
                    return CheckResult(self.name, CheckStatus.FAIL, "No tools registered")

                tools_without_desc = [
                    t.get("name", "<unknown>")
                    for t in tools
                    if not t.get("description") or len(t["description"].strip()) < 10
                ]

                if tools_without_desc:
                    return CheckResult(
                        self.name,
                        CheckStatus.WARN,
                        f"Tools missing description: {', '.join(tools_without_desc)}",
                    )

                return CheckResult(self.name, CheckStatus.PASS, "All tools have descriptions")

        except Exception:
            log.exception("ToolDescriptionQualityCheck crashed (project=%s, command=%s)", ctx.project_path, command)
            tail = s.runner.stderr_tail if "s" in locals() else ""
            extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
            return CheckResult(self.name, CheckStatus.FAIL, f"Exception during tool description check{extra}")
