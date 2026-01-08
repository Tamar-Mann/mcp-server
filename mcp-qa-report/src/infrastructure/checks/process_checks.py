from domain.models import CheckResult, CheckStatus
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
import logging

log = logging.getLogger(__name__)

class MCPServerStartupCheck:
    """
    Verifies that the MCP server can be started and responds correctly
    to the initial 'initialize' JSON-RPC request.

    This ensures the server is runnable and speaks valid MCP over STDIO.
    """
    name = "MCP server starts and responds over stdio"

    def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                "Cannot determine how to start MCP server. "
                "Provide an explicit 'command' parameter (e.g. ['python', '-m', 'mcp_server.server'])."
            )

        factory = ctx.runner_factory or RunnerFactory()

        try:
            with factory.create(command, ctx.project_path, ctx.timeout_sec) as s:
                data = s.client.initialize()
                if not data or "result" not in data:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"No valid initialize response received from server{extra}")

                return CheckResult(self.name, CheckStatus.PASS, "Server responded to initialize")

        except Exception:
            log.exception("MCPServerStartupCheck crashed (project=%s, command=%s)", ctx.project_path, command)
            tail = s.runner.stderr_tail if "s" in locals() else ""
            extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
            return CheckResult(self.name, CheckStatus.FAIL, f"Exception during startup{extra}")
