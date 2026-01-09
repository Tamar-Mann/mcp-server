import pytest
from application.execution_context import ExecutionContext
from infrastructure.checks.stdio_checks import STDIOIntegrityCheck
from domain.models import CheckStatus


@pytest.mark.asyncio
async def test_stdio_integrity_fails_on_noise(ctx_factory, fake_session):
    fake_session.client.initialize_collect_noise.return_value = (
        {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}, ["NOISE"]
    )
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await STDIOIntegrityCheck().run(ctx)
    assert res.status == CheckStatus.FAIL
    assert "Unexpected STDIO output" in res.message


@pytest.mark.asyncio
async def test_stdio_integrity_passes_when_clean(ctx_factory, fake_session):
    fake_session.client.initialize_collect_noise.return_value = (
        {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}, []
    )
    ctx = ExecutionContext(
        project_path=".",
        command=["python", "-m", "x"],
        runner_factory=ctx_factory,
    )
    res = await STDIOIntegrityCheck().run(ctx)
    assert res.status == CheckStatus.PASS