import subprocess
import json
import time
from typing import Optional


class MCPProcessRunner:
    def __init__(self, command: list[str], project_path: str, timeout_sec: int):
        self._command = command
        self._project_path = project_path
        self._timeout = timeout_sec
        self._proc: Optional[subprocess.Popen] = None

    def initialize(self) -> Optional[dict]:
        self._proc = subprocess.Popen(
            self._command,
            cwd=self._project_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "qa-check",
                    "version": "0.1.0",
                },
            },
        }

        assert self._proc.stdin is not None
        assert self._proc.stdout is not None

        self._proc.stdin.write(json.dumps(init_msg) + "\n")
        self._proc.stdin.flush()

        deadline = time.time() + self._timeout

        # קריאה blocking ל-stdout (קרוס-פלטפורם, ללא select)
        while time.time() < deadline:
            line = self._proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue

            line = line.strip()
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # רעש STDIO – מתעלמים

            if data.get("jsonrpc") == "2.0" and "result" in data:
                return data

        return None

    def terminate(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.terminate()



    def peek_stdout(self, timeout: float = 0.1) -> str | None:
        """
        Peek at stdout without sending any input.
        Used to detect unexpected STDIO noise before initialize.
        """
        if not self._proc or not self._proc.stdout:
            return None

        start = time.time()
        while time.time() - start < timeout:
            line = self._proc.stdout.readline()
            if line:
                return line.strip()
            time.sleep(0.01)

        return None


    def send_request(self, method: str, request_id: int) -> dict | None:
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            return None

        msg = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": {},
        }

        self._proc.stdin.write(json.dumps(msg) + "\n")
        self._proc.stdin.flush()

        deadline = time.time() + self._timeout
        while time.time() < deadline:
            line = self._proc.stdout.readline()
            if not line:
                continue
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            if data.get("id") == request_id:
                return data

        return None
