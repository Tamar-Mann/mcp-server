from application.execution_context import ExecutionContext
from infrastructure.checks.stdio_checks import STDIOIntegrityCheck
from domain.models import CheckStatus


class FakeClient:
    def __init__(self, init_resp, noise):
        self._init_resp = init_resp
        self._noise = noise

    def initialize_collect_noise(self):
        return self._init_resp, self._noise


class FakeRunner:
    stderr_tail = "stderr tail"


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


def test_stdio_integrity_fails_on_noise():
    init = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(init, ["NOISE"]))),
    )
    res = STDIOIntegrityCheck().run(ctx)
    assert res.status == CheckStatus.FAIL
    assert "Unexpected STDIO output" in res.message


def test_stdio_integrity_passes_when_clean():
    init = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=FakeFactory(FakeSession(FakeClient(init, []))),
    )
    res = STDIOIntegrityCheck().run(ctx)
    assert res.status == CheckStatus.PASS
