from domain.models import CheckResult, CheckStatus
from infrastructure.process_runner import MCPProcessRunner
from infrastructure.detect_mcp import detect_mcp_command
import json

class ToolsRegistrationCheck:
    name = "MCP tools are registered and discoverable"

    def run(self, ctx) -> CheckResult:
        command = ctx.command or detect_mcp_command(ctx.project_path)
        if not command:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                "Cannot determine MCP start command",
            )

        try:
            with MCPProcessRunner(
                command=command,
                project_path=ctx.project_path,
                timeout_sec=ctx.timeout_sec,
            ) as runner:
                # initialize
                if not runner.initialize():
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        "Server did not respond to initialize",
                    )

                # tools/list
                response = runner.send_request(
                    method="tools/list",
                    request_id=2,
                )

                if not response or "result" not in response:
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        "tools/list returned no result",
                    )

                tools = response["result"].get("tools", [])
                if not tools:
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        "No tools registered",
                    )

                for tool in tools:
                    if "name" not in tool or "inputSchema" not in tool:
                        return CheckResult(
                            self.name,
                            CheckStatus.FAIL,
                            f"Invalid tool schema: {tool}",
                        )

                return CheckResult(
                    self.name,
                    CheckStatus.PASS,
                    f"{len(tools)} tools registered correctly",
                )

        except Exception as e:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"Exception during tools check: {e}",
            )
