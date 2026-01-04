from application.execution_context import ExecutionContext
from infrastructure.checks.tool_quality_checks import ToolDescriptionQualityCheck
from domain.models import CheckStatus


class FakeClient:
    def __init__(self, tools_list_resp):
        self._tools_list_resp = tools_list_resp

    def initialize(self):
        return {"jsonrpc": "2.0", "id": 1, "result": {}}

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


def test_tool_description_quality_warns_on_missing_desc():
    tools = {
        "jsonrpc": "2.0",
        "id": 10,
        "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "  "}]},
    }

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(tools))),
    )
    res = ToolDescriptionQualityCheck().run(ctx)
    assert res.status == CheckStatus.WARN
    assert "Tools missing description" in res.message


def test_tool_description_quality_passes_when_all_have_desc():
    tools = {
        "jsonrpc": "2.0",
        "id": 10,
        "result": {"tools": [{"name": "t1", "inputSchema": {}, "description": "Nice description"}]},
    }

    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(tools))),
    )
    res = ToolDescriptionQualityCheck().run(ctx)
    assert res.status == CheckStatus.PASS
