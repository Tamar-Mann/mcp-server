from application.execution_context import ExecutionContext
from infrastructure.checks.tool_checks import ToolsRegistrationCheck
from domain.models import CheckStatus


class FakeClient:
    def __init__(self, init_resp, tools_list_resp):
        self._init_resp = init_resp
        self._tools_list_resp = tools_list_resp

    def initialize(self):
        return self._init_resp

    def call(self, method, request_id, params=None):
        assert method == "tools/list"
        return self._tools_list_resp


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


def test_tools_registration_fails_on_invalid_schema():
    init = {"jsonrpc": "2.0", "id": 1, "result": {}}
    tools = {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "x"}]}}  # missing inputSchema

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(init, tools))),
    )
    res = ToolsRegistrationCheck().run(ctx)
    assert res.status == CheckStatus.FAIL


def test_tools_registration_passes_on_valid_tools():
    init = {"jsonrpc": "2.0", "id": 1, "result": {}}
    tools = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "good enough"}]},
    }

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(init, tools))),
    )
    res = ToolsRegistrationCheck().run(ctx)
    assert res.status == CheckStatus.PASS
