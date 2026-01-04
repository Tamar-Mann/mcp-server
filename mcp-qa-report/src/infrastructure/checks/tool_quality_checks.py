from domain.models import CheckResult, CheckStatus
from infrastructure.process_runner import MCPProcessRunner
from infrastructure.detect_mcp import detect_mcp_command


class ToolDescriptionQualityCheck:
    name = "Tool description quality"

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

                if not runner.initialize():
                    return CheckResult(
                        self.name,
                        CheckStatus.FAIL,
                        "Server did not respond to initialize",
                    )

                response = runner.send_request(
                    method="tools/list",
                    request_id=10,
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

                tools_without_desc = [
                    t["name"]
                    for t in tools
                    if not t.get("description")
                    or len(t["description"].strip()) < 10
                ]

                if tools_without_desc:
                    return CheckResult(
                        self.name,
                        CheckStatus.WARN,
                        f"Tools missing description: {', '.join(tools_without_desc)}",
                    )

                return CheckResult(
                    self.name,
                    CheckStatus.PASS,
                    "All tools have descriptions",
                )

        except Exception as e:
            return CheckResult(
                self.name,
                CheckStatus.FAIL,
                f"Exception during tool description check: {e}",
            )
