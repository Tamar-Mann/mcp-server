from pathlib import Path

from domain.models import CheckResult, CheckStatus
import pytest
import asyncio


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, name: str, description: str | None = None):
        def deco(fn):
            self.tools[name] = fn
            return fn
        return deco


class DummyRunner:
    async def run(self, ctx):
        return [CheckResult("x", CheckStatus.PASS, "ok")]


class DummyReporter:
    def render(self, results):
        return "REPORT"


@pytest.mark.asyncio
async def test_qa_report_writes_to_directory(tmp_path: Path, monkeypatch):
    from mcp_server import tools as tools_mod

    fake = FakeMCP()
    tools_mod.register(fake)

    monkeypatch.setattr(tools_mod, "build_runner", lambda fail_fast: DummyRunner())
    monkeypatch.setattr(tools_mod, "build_reporter", lambda: DummyReporter())

    # Await the async qa_report tool handler
    res = await fake.tools["qa_report"](project_path=str(tmp_path), output_path="out/")
    assert "Wrote report to:" in res

    p = tmp_path / "out" / "qa_report.txt"
    assert p.exists()
    assert p.read_text(encoding="utf-8") == "REPORT"


@pytest.mark.asyncio
async def test_qa_report_writes_to_explicit_file(tmp_path: Path, monkeypatch):
    from mcp_server import tools as tools_mod

    fake = FakeMCP()
    tools_mod.register(fake)

    monkeypatch.setattr(tools_mod, "build_runner", lambda fail_fast: DummyRunner())
    monkeypatch.setattr(tools_mod, "build_reporter", lambda: DummyReporter())

    # Await the async qa_report tool handler
    res = await fake.tools["qa_report"](project_path=str(tmp_path), output_path="out/custom.md")
    assert "Wrote report to:" in res

    p = tmp_path / "out" / "custom.md"
    assert p.exists()
    assert p.read_text(encoding="utf-8") == "REPORT"
