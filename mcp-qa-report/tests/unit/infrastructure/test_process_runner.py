import io
import os
import subprocess
from pathlib import Path

from infrastructure.process_runner import MCPProcessRunner


class DummyPopen:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pid = 1234
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr = io.StringIO("e1\ne2\ne3\n")
        self._alive = True

    def poll(self):
        return None if self._alive else 0

    def terminate(self):
        self._alive = False

    def kill(self):
        self._alive = False

    def wait(self, timeout=None):
        self._alive = False
        return 0


def test_start_sets_pythonpath_when_src_exists(tmp_path: Path, monkeypatch):
    (tmp_path / "src").mkdir()
    captured = {}

    def fake_popen(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return DummyPopen(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    runner = MCPProcessRunner(command=["python", "-m", "x"], project_path=str(tmp_path))
    runner.start()

    env = captured["kwargs"]["env"]
    assert "PYTHONPATH" in env
    assert str(tmp_path / "src") in env["PYTHONPATH"]

    runner.terminate()


def test_stderr_tail_keeps_last_lines(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: DummyPopen(*a, **k))

    runner = MCPProcessRunner(command=["python", "-m", "x"], project_path=str(tmp_path))
    runner.start()
    runner.terminate()

    tail = runner.stderr_tail
    assert "e1" in tail and "e3" in tail
