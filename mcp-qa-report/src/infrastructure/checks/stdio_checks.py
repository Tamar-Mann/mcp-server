from domain.models import CheckResult, CheckStatus
from infrastructure.process_runner import MCPProcessRunner
from infrastructure.detect_mcp import detect_mcp_command

class STDIOIntegrityCheck:
    name = "STDIO integrity (no noise before initialize)"

    def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                "Cannot determine MCP start command",
            )

        with MCPProcessRunner(
            command=command,
            project_path=ctx.project_path,
            timeout_sec=ctx.timeout_sec,
        ) as runner:
            # כאן: לקרוא stdout לפני initialize
            noise = runner.peek_stdout(timeout=0.2)
            if noise:
                return CheckResult(
                    self.name,
                    CheckStatus.FAIL,
                    f"Unexpected STDIO output before initialize: {noise[:80]}",
                )

            return CheckResult(
                self.name,
                CheckStatus.PASS,
                "STDIO clean before initialize",
            )
