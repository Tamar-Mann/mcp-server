from domain.models import CheckResult, CheckStatus
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
import logging

log = logging.getLogger(__name__)

class ToolsRegistrationCheck:
    """
    Validates that the MCP server registers tools correctly
    and that each tool exposes a minimal valid schema
    (name and inputSchema).

    This confirms tools are discoverable via tools/list.
    """
    name = "MCP tools are registered and discoverable"

    async def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(self.name, CheckStatus.FAIL, "Cannot determine MCP start command")

        factory = ctx.runner_factory or RunnerFactory()

        try:
            async with factory.create(command, ctx.project_path, ctx.timeout_sec) as s:
                init = await s.client.initialize()
                if not init or "result" not in init:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"Server did not respond to initialize{extra}")

                response = await s.client.call("tools/list", request_id=2)
                if not response or "result" not in response:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"tools/list returned no result{extra}")

                tools = response["result"].get("tools", [])
                if not tools:
                    return CheckResult(self.name, CheckStatus.FAIL, "No tools registered")

                for tool in tools:
                    if "name" not in tool or "inputSchema" not in tool:
                        return CheckResult(self.name, CheckStatus.FAIL, f"Invalid tool schema: {tool}")

                return CheckResult(self.name, CheckStatus.PASS, f"{len(tools)} tools registered correctly")

        except Exception:
            log.exception("ToolsRegistrationCheck crashed (project=%s, command=%s)", ctx.project_path, command)
            tail = ""
            if 's' in locals() and s is not None:
                try:
                    tail = s.runner.stderr_tail
                except Exception:
                    pass
            
            extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
            return CheckResult(self.name, CheckStatus.FAIL, f"Exception during tools check{extra}")