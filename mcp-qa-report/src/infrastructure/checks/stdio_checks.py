from domain.models import CheckResult, CheckStatus
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
import logging

log = logging.getLogger(__name__)

class STDIOIntegrityCheck:
    """
    Ensures the MCP server does not emit any unexpected output
    to STDIO before responding to the 'initialize' request.

    Any noise before initialization may break JSON-RPC communication.
    """
    name = "STDIO integrity (no noise before initialize)"

    async def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(self.name, CheckStatus.FAIL, "Cannot determine MCP start command")

        factory = ctx.runner_factory or RunnerFactory()

        try:
            async with factory.create(command, ctx.project_path, ctx.timeout_sec) as s:
                init_response, noise = await s.client.initialize_collect_noise()

                if not init_response or "result" not in init_response:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"Server did not respond to initialize{extra}")

                if noise:
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        f"Unexpected STDIO output before initialize: {noise[0][:80]}",
                    )

                return CheckResult(self.name, CheckStatus.PASS, "STDIO clean before initialize")

        except Exception:
            log.exception("STDIOIntegrityCheck crashed (project=%s, command=%s)", ctx.project_path, command)
            tail = ""
            if 's' in locals() and s is not None:
                try:
                    tail = s.runner.stderr_tail
                except Exception:
                    pass
            
            extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
            return CheckResult(self.name, CheckStatus.FAIL, f"Exception during STDIO check{extra}")