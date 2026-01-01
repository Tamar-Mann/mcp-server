from infrastructure.detect_mcp import detect_mcp_command
from domain.models import CheckResult, CheckStatus
from infrastructure.process_runner import MCPProcessRunner

class MCPServerStartupCheck:
    name = "MCP server starts and responds over stdio"

    def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                "Cannot determine how to start MCP server",
            )

        try:
            with MCPProcessRunner(
                command=command,
                project_path=ctx.project_path,
                timeout_sec=ctx.timeout_sec,
            ) as runner:
                data = runner.initialize()
                if not data:
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        "No response received from server",
                    )

                return CheckResult(
                    self.name,
                    CheckStatus.PASS,
                    "Server responded to initialize",
                )

        except Exception as e:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"Exception during startup: {e}",
            )
