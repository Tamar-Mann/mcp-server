import io
import json
import pytest

from infrastructure.jsonrpc_client import JsonRpcClient
from infrastructure.errors import JsonRpcTimeoutError, JsonRpcProtocolError


class ExplodingStdin:
    def write(self, _):
        raise OSError("nope")

    def flush(self):
        pass


def test_initialize_success_reads_matching_id():
    stdout = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}) + "\n")
    stdin = io.StringIO()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp = c.initialize()
        assert resp["result"]["ok"] is True
    finally:
        c.close()


def test_initialize_collects_noise_for_non_json_lines():
    out = "\n".join([
        "HELLO THERE",
        json.dumps({"jsonrpc": "2.0", "method": "notifications/message", "params": {"x": 1}}),
        json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}),
        "",
    ])
    stdout = io.StringIO(out)
    stdin = io.StringIO()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp, noise = c.initialize_collect_noise()
        assert resp["result"]["ok"] is True
        assert noise and noise[0] == "HELLO THERE"
    finally:
        c.close()


def test_call_ignores_other_ids_and_waits_for_expected():
    out = "\n".join([
        json.dumps({"jsonrpc": "2.0", "id": 999, "result": {"no": "this"}}),
        json.dumps({"jsonrpc": "2.0", "id": 20, "result": {"tools": []}}),
        "",
    ])
    stdout = io.StringIO(out)
    stdin = io.StringIO()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=1)
    try:
        resp = c.call("tools/list", request_id=20)
        assert resp["result"]["tools"] == []
    finally:
        c.close()


def test_timeout_raises():
    stdout = io.StringIO("")  # EOF immediately
    stdin = io.StringIO()
    c = JsonRpcClient(stdin=stdin, stdout=stdout, timeout_sec=0.2)
    try:
        with pytest.raises(JsonRpcTimeoutError):
            c.initialize()
    finally:
        c.close()


def test_protocol_error_on_write_failure():
    stdout = io.StringIO("")
    c = JsonRpcClient(stdin=ExplodingStdin(), stdout=stdout, timeout_sec=0.2)
    try:
        with pytest.raises(JsonRpcProtocolError):
            c.initialize()
    finally:
        c.close()
