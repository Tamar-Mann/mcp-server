from application.execution_context import ExecutionContext
from infrastructure.checks.invocation_checks import ToolInvocationCheck
from domain.models import CheckStatus


class FakeClient:
    def __init__(self, tools, call_resp):
        self._tools = tools
        self._call_resp = call_resp

    def initialize(self):
        return {"jsonrpc": "2.0", "id": 1, "result": {}}

    def call(self, method, request_id, params=None):
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": self._tools}}
        if method == "tools/call":
            return self._call_resp
        raise AssertionError("unexpected method")


class FakeRunner:
    stderr_tail = ""


class FakeSession:
    def __init__(self, client):
        self.runner = FakeRunner()
        self._client = client

    def __enter__(self):
        return self

    @property
    def client(self):
        return self._client

    def __exit__(self, exc_type, exc, tb):
        return None


class FakeFactory:
    def __init__(self, session):
        self._session = session

    def create(self, command, project_path, timeout_sec):
        return self._session


def test_invocation_warns_when_no_ping():
    tools = [{"name": "qa_report", "inputSchema": {}, "description": "x"}]
    client = FakeClient(tools=tools, call_resp=None)
    ctx = ExecutionContext(project_path=".", command=["python"], runner_factory=FakeFactory(FakeSession(client)))

    res = ToolInvocationCheck().run(ctx)
    assert res.status == CheckStatus.WARN
    assert "No ping tool" in res.message


def test_invocation_passes_when_ping_exists_and_call_ok():
    tools = [{"name": "ping", "inputSchema": {}, "description": "Health check tool. Returns ok."}]
    call_resp = {"jsonrpc": "2.0", "id": 30, "result": {"content": [{"type": "text", "text": "ok"}]}}

    client = FakeClient(tools=tools, call_resp=call_resp)
    ctx = ExecutionContext(project_path=".", command=["python"], runner_factory=FakeFactory(FakeSession(client)))

    res = ToolInvocationCheck().run(ctx)
    assert res.status == CheckStatus.PASS
