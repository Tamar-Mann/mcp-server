import os
import logging
from pathlib import Path
import subprocess
import threading
from collections import deque
from typing import Optional, TextIO

log = logging.getLogger(__name__)


class MCPProcessRunner:
    def __init__(self, command: list[str], project_path: str):
        self._command = command
        self._project_path = project_path
        self._proc: Optional[subprocess.Popen[str]] = None

        self._stderr_lines = deque(maxlen=200)
        self._stderr_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            return

        cwd = Path(self._project_path)

        env = os.environ.copy()
        src_dir = cwd / "src"
        if src_dir.exists():
            existing = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(src_dir) + (os.pathsep + existing if existing else "")

        try:
            self._proc = subprocess.Popen(
                self._command,
                cwd=self._project_path,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # line-buffered-ish for text streams
            )
        except Exception:
            # Minimal log, but with stacktrace for debugging
            log.exception(
                "MCPProcessRunner failed to start (cwd=%s, command=%s)",
                self._project_path,
                self._command,
            )
            raise

        # Minimal debug (no env dump)
        log.debug(
            "MCPProcessRunner started pid=%s cwd=%s command=%s",
            self._proc.pid,
            self._project_path,
            self._command,
        )

        stderr = self._proc.stderr
        if stderr is not None:
            self._stderr_thread = threading.Thread(
                target=self._drain_stderr,
                args=(stderr,),
                daemon=True,
            )
            self._stderr_thread.start()

    def _drain_stderr(self, stderr: TextIO) -> None:
        try:
            for line in stderr:
                self._stderr_lines.append(line.rstrip("\n"))
        except Exception:
            # Do not spam logs; stderr draining is best-effort
            pass

    @property
    def stderr_tail(self) -> str:
        return "\n".join(list(self._stderr_lines)[-20:])

    @property
    def stdin(self) -> TextIO:
        assert self._proc is not None and self._proc.stdin is not None
        return self._proc.stdin

    @property
    def stdout(self) -> TextIO:
        assert self._proc is not None and self._proc.stdout is not None
        return self._proc.stdout

    def terminate(self) -> None:
        proc = self._proc
        if proc is None:
            return

        log.debug("MCPProcessRunner terminating pid=%s", proc.pid)

        try:
            # Closing stdin often helps the child process exit gracefully
            try:
                if proc.stdin:
                    proc.stdin.close()
            except Exception:
                pass

            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    log.debug("MCPProcessRunner kill pid=%s (terminate timeout)", proc.pid)
                    proc.kill()
                    try:
                        proc.wait(timeout=1)
                    except Exception:
                        pass

        finally:
            # Close pipes so reader threads (stdout/stderr) can unblock on EOF
            for stream in (proc.stdout, proc.stderr):
                try:
                    if stream:
                        stream.close()
                except Exception:
                    pass

            if self._stderr_thread:
                self._stderr_thread.join(timeout=0.5)
                self._stderr_thread = None

            self._proc = None

    def __enter__(self) -> "MCPProcessRunner":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.terminate()
