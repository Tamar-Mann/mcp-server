from domain.models import CheckResult, CheckStatus
from infrastructure.detect_mcp import detect_mcp_command
from infrastructure.runner_factory import RunnerFactory
import logging

log = logging.getLogger(__name__)

class ToolInvocationCheck:
    """
    Performs an end-to-end invocation test using tools/call.

    If a safe tool such as 'ping' exists, it is invoked to verify
    full request/response flow. If no safe tool is available,
    the check degrades gracefully to WARN.
    """    
    name = "MCP tool invocation works (tools/call)"

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

                list_resp = await s.client.call("tools/list", request_id=20)
                if not list_resp or "result" not in list_resp:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"tools/list returned no result{extra}")

                tools = list_resp["result"].get("tools", [])
                if not tools:
                    return CheckResult(self.name, CheckStatus.FAIL, "No tools registered")

                has_ping = any(t.get("name") == "ping" for t in tools)
                if not has_ping:
                    return CheckResult(self.name, CheckStatus.WARN, "No ping tool; skipping invocation test")

                resp = await s.client.call(
                    "tools/call",
                    request_id=30,
                    params={"name": "ping", "arguments": {}},
                )

                if not resp:
                    tail = s.runner.stderr_tail
                    extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
                    return CheckResult(self.name, CheckStatus.FAIL, f"tools/call returned no response{extra}")

                if "error" in resp:
                    return CheckResult(self.name, CheckStatus.FAIL, f"tools/call error: {resp['error']}")

                if "result" not in resp:
                    return CheckResult(self.name, CheckStatus.WARN, f"tools/call returned unexpected response: {resp}")

                return CheckResult(self.name, CheckStatus.PASS, "tools/call executed successfully (ping)")

        except Exception:
            log.exception("ToolInvocationCheck crashed (project=%s, command=%s)", ctx.project_path, command)
            tail = ""
            if 's' in locals() and s is not None:
                tail = s.runner.stderr_tail
            extra = f"\n--- stderr tail ---\n{tail}" if tail else ""
            return CheckResult(self.name, CheckStatus.FAIL, f"Exception during tools/call{extra}")