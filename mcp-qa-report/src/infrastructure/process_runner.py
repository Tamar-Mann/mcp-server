"""
Subprocess runner for stdio-based MCP servers.

Starts a target MCP server as a subprocess, wires stdin/stdout for JSON-RPC,
drains stderr in an async task (avoids blocking), and exposes a stderr tail for debugging.
"""
import os
import logging
from pathlib import Path
import asyncio
from collections import deque
from typing import Optional

log = logging.getLogger(__name__)

class MCPProcessRunner:
    """Manages lifecycle of a subprocess MCP server (stdio), including async stderr draining."""
    def __init__(self, command: list[str], project_path: str):
        self._command = command
        self._project_path = project_path
        self._proc: Optional[asyncio.subprocess.Process] = None

        self._stderr_lines = deque(maxlen=200)
        self._stderr_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._proc is not None:
            if self._proc.returncode is None:
                return

        cwd = Path(self._project_path)

        env = os.environ.copy()
        src_dir = cwd / "src"
        if src_dir.exists():
            existing = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(src_dir) + (os.pathsep + existing if existing else "")

        try:
            self._proc = await asyncio.create_subprocess_exec(
                *self._command,
                cwd=self._project_path,
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception:
            log.exception(
                "MCPProcessRunner failed to start (cwd=%s, command=%s)",
                self._project_path,
                self._command,
            )
            raise

        log.debug(
            "MCPProcessRunner started pid=%s cwd=%s command=%s",
            self._proc.pid,
            self._project_path,
            self._command,
        )

        if self._proc.stderr is not None:
            # Non-blocking drain of stderr to capture server logs without stalling the event loop
            self._stderr_task = asyncio.create_task(self._drain_stderr(self._proc.stderr))

    async def _drain_stderr(self, stderr: asyncio.StreamReader) -> None:
        try:
            while True:
                line = await stderr.readline()
                if not line:
                    break
                self._stderr_lines.append(line.decode("utf-8", errors="replace").rstrip("\n"))
        except Exception:
            pass

    @property
    def stderr_tail(self) -> str:
        return "\n".join(list(self._stderr_lines)[-20:])

    @property
    def stdin(self) -> asyncio.StreamWriter:
        assert self._proc is not None and self._proc.stdin is not None
        return self._proc.stdin

    @property
    def stdout(self) -> asyncio.StreamReader:
        assert self._proc is not None and self._proc.stdout is not None
        return self._proc.stdout

    async def terminate(self) -> None:
        proc = self._proc
        if proc is None:
            return

        log.debug("MCPProcessRunner terminating pid=%s", proc.pid)

        try:
            if proc.stdin is not None:
                try:
                    proc.stdin.close()
                    await proc.stdin.wait_closed()
                except Exception:
                    pass

            if proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    log.debug("MCPProcessRunner kill pid=%s (terminate timeout)", proc.pid)
                    proc.kill()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=1.0)
                    except Exception:
                        pass

        finally:
            if self._stderr_task is not None:
                try:
                    self._stderr_task.cancel()
                    await self._stderr_task
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass
                self._stderr_task = None

            self._proc = None

    async def __aenter__(self) -> "MCPProcessRunner":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.terminate()
