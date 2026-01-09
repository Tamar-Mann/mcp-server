import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.process_runner import MCPProcessRunner


class DummyAsyncProcess:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pid = 1234
        self.stdin = MagicMock()
        self.stdin.close = MagicMock()
        self.stdin.wait_closed = AsyncMock()
        self.stdout = AsyncMock()
        self.stderr = AsyncMock()
        self.returncode = None
        self._alive = True

    async def wait(self):
        self.returncode = 0
        self._alive = False
        return 0

    def terminate(self):
        self._alive = False
        self.returncode = -15

    def kill(self):
        self._alive = False
        self.returncode = -9


@pytest.mark.asyncio
async def test_start_sets_pythonpath_when_src_exists(tmp_path: Path):
    (tmp_path / "src").mkdir()
    captured = {}

    async def fake_create_subprocess_exec(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        proc = DummyAsyncProcess(*args, **kwargs)
        proc.stderr = AsyncMock()
        proc.stderr.readline = AsyncMock(side_effect=[b"e1\n", b"e2\n", b"e3\n", b""])
        return proc

    with patch("asyncio.create_subprocess_exec", side_effect=fake_create_subprocess_exec):
        runner = MCPProcessRunner(command=["python", "-m", "x"], project_path=str(tmp_path))
        await runner.start()

        env = captured["kwargs"]["env"]
        assert "PYTHONPATH" in env
        assert str(tmp_path / "src") in env["PYTHONPATH"]

        await runner.terminate()


@pytest.mark.asyncio
async def test_stderr_tail_keeps_last_lines(tmp_path: Path):
    async def fake_create_subprocess_exec(*args, **kwargs):
        proc = DummyAsyncProcess(*args, **kwargs)
        proc.stderr = AsyncMock()
        proc.stderr.readline = AsyncMock(side_effect=[b"e1\n", b"e2\n", b"e3\n", b""])
        return proc

    with patch("asyncio.create_subprocess_exec", side_effect=fake_create_subprocess_exec):
        runner = MCPProcessRunner(command=["python", "-m", "x"], project_path=str(tmp_path))
        await runner.start()
        await runner.terminate()

        tail = runner.stderr_tail
        assert "e1" in tail and "e3" in tail
