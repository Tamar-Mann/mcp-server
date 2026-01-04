import json
import time
import threading
import queue
from typing import TextIO

from infrastructure.errors import JsonRpcTimeoutError, JsonRpcProtocolError


class JsonRpcClient:
    def __init__(self, stdin: TextIO, stdout: TextIO, timeout_sec: int):
        self._stdin = stdin
        self._stdout = stdout
        self._timeout = timeout_sec

        self._q: "queue.Queue[str]" = queue.Queue()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._reader, daemon=True)
        self._t.start()

    def _reader(self) -> None:
        # Reads stdout lines forever and pushes to queue (no blocking in main thread)
        while not self._stop.is_set():
            line = self._stdout.readline()
            if not line:
                # EOF or process ended
                break
            self._q.put(line)

    def close(self) -> None:
        self._stop.set()
        try:
            self._t.join(timeout=0.2)
        except Exception:
            pass


    def initialize(self) -> dict | None:
        data, _ = self._request_with_optional_noise(self._init_msg(), expected_id=1, collect_noise=False)
        return data

    def initialize_collect_noise(self) -> tuple[dict | None, list[str]]:
        return self._request_with_optional_noise(self._init_msg(), expected_id=1, collect_noise=True)

    def call(self, method: str, request_id: int, params: dict | None = None) -> dict | None:
        msg = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        data, _ = self._request_with_optional_noise(msg, expected_id=request_id, collect_noise=False)
        return data

    def _init_msg(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "qa-check", "version": "0.1.0"},
            },
        }

    def _write_json(self, msg: dict) -> None:
        try:
            self._stdin.write(json.dumps(msg) + "\n")
            self._stdin.flush()
        except Exception as e:
            raise JsonRpcProtocolError(f"Failed writing JSON-RPC request: {e}") from e

    def _request_with_optional_noise(
        self,
        msg: dict,
        expected_id: int,
        collect_noise: bool,
    ) -> tuple[dict | None, list[str]]:
        self._write_json(msg)

        noise: list[str] = []
        deadline = time.time() + self._timeout

        while time.time() < deadline:
            remaining = max(0.0, deadline - time.time())
            try:
                line = self._q.get(timeout=min(0.2, remaining))
            except queue.Empty:
                continue

            s = line.strip()
            if not s:
                continue

            try:
                data = json.loads(s)
            except json.JSONDecodeError:
                if collect_noise:
                    noise.append(s)
                continue

            # Accept only proper response with matching id
            if data.get("jsonrpc") == "2.0" and data.get("id") == expected_id:
                if "result" in data or "error" in data:
                    return data, noise

            # Notifications/other responses: ignore (or store as noise if you want)

        raise JsonRpcTimeoutError(f"Timeout waiting for JSON-RPC response id={expected_id}")
