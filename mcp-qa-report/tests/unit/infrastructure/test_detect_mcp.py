import json
from pathlib import Path

from infrastructure.detect_mcp import detect_mcp_command


def test_detect_prefers_vscode_mcp_json_servers_stdio(tmp_path: Path):
    root = tmp_path
    (root / ".vscode").mkdir()
    cfg = {
        "servers": {
            "a": {"type": "http", "command": "node", "args": ["x"]},
            "b": {"type": "stdio", "command": "python", "args": ["-m", "mcp_server.server"]},
        }
    }
    (root / ".vscode" / "mcp.json").write_text(json.dumps(cfg), encoding="utf-8")

    cmd = detect_mcp_command(str(root))
    assert cmd == ["python", "-m", "mcp_server.server"]


def test_detect_accepts_mcpServers_key(tmp_path: Path):
    root = tmp_path
    cfg = {"mcpServers": {"s1": {"type": "stdio", "command": "python", "args": ["-m", "x"]}}}
    (root / "mcp.json").write_text(json.dumps(cfg), encoding="utf-8")

    cmd = detect_mcp_command(str(root))
    assert cmd == ["python", "-m", "x"]


def test_detect_mcp_json_args_not_list_becomes_empty(tmp_path: Path):
    root = tmp_path
    cfg = {"servers": {"s1": {"type": "stdio", "command": "python", "args": "oops"}}}
    (root / "mcp.json").write_text(json.dumps(cfg), encoding="utf-8")

    cmd = detect_mcp_command(str(root))
    assert cmd == ["python"]


def test_detect_from_pyproject_single_script_entrypoint_module_func(tmp_path: Path, monkeypatch):
    root = tmp_path
    pyproject = """
[project]
name = "x"
version = "0.1.0"
[project.scripts]
qa-report-mcp = "mcp_server.server:main"
"""
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    monkeypatch.setattr("infrastructure.detect_mcp.sys.executable", "python")

    cmd = detect_mcp_command(str(root))
    assert cmd[0:2] == ["python", "-c"]
    assert "importlib.import_module('mcp_server.server')" in cmd[2]
    assert "getattr(m,'main')()" in cmd[2]


def test_detect_from_package_json_start(tmp_path: Path):
    root = tmp_path
    pkg = {"scripts": {"start": "node server.js"}}
    (root / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

    cmd = detect_mcp_command(str(root))
    assert cmd == ["npm", "run", "start"]


def test_detect_none_when_no_configs(tmp_path: Path):
    assert detect_mcp_command(str(tmp_path)) is None
