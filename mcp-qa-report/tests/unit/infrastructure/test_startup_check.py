from application.execution_context import ExecutionContext
from infrastructure.checks.process_checks import MCPServerStartupCheck
from domain.models import CheckStatus


class FakeClient:
    def __init__(self, init_resp):
        self._init_resp = init_resp

    def initialize(self):
        return self._init_resp


class FakeRunner:
    stderr_tail = "stderr tail here"


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


def test_startup_check_fails_when_no_command_and_detect_none(monkeypatch):
    monkeypatch.setattr("infrastructure.checks.process_checks.detect_mcp_command", lambda _: None)
    ctx = ExecutionContext(project_path=".")
    res = MCPServerStartupCheck().run(ctx)
    assert res.status == CheckStatus.FAIL


def test_startup_check_passes_on_initialize_result():
    init = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    session = FakeSession(FakeClient(init))
    ctx = ExecutionContext(project_path=".", command=["python", "-m", "x"], runner_factory=FakeFactory(session))
    res = MCPServerStartupCheck().run(ctx)
    assert res.status == CheckStatus.PASS
