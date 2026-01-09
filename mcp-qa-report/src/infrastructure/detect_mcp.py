"""
Detects how to start a target MCP server project.

Prefers explicit MCP config (mcp.json / .vscode/mcp.json),
then falls back to Python entrypoints (pyproject scripts) or Node scripts (package.json).
Returns a command list suitable for subprocess execution, or None if unknown.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import tomllib
from typing import Any

def _pick_entrypoint(scripts: dict[str, Any]) -> str | None:
    if not scripts:
        return None

    if len(scripts) == 1:
        return next(iter(scripts.values()))

    # Prefer common “server-ish” names if multiple exist
    preferred_names = ("mcp", "server", "serve", "start", "run")
    for k, v in scripts.items():
        if any(p in k.lower() for p in preferred_names):
            return v

    # Fallback: first item
    return next(iter(scripts.values()))


def _command_from_entrypoint(entrypoint: Any) -> list[str] | None:
    if not isinstance(entrypoint, str):
        return None
    ep = entrypoint.strip()
    if not ep:
        return None

    # Using 'uv run' ensures the correct virtual environment is used
    # even if we are running from a different project context.
    base_cmd = ["uv", "run", "python"]

    # "pkg.mod:main"
    if ":" in ep:
        module, func = ep.split(":", 1)
        module = module.strip()
        func = func.strip()
        if not module or not func:
            return None

        # Run callable directly
        code = (
            "import importlib;"
            f"m=importlib.import_module('{module}');"
            f"getattr(m,'{func}')()"
        )
        return [*base_cmd, "-c", code]

    # "pkg.mod" only
    return [*base_cmd, "-m", ep]


def detect_mcp_command(project_path: str) -> list[str] | None:
    root = Path(project_path)

    # 0) Prefer explicit MCP config (source of truth)
    for cfg in (root / ".vscode" / "mcp.json", root / "mcp.json"):
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))

                servers = data.get("servers") or data.get("mcpServers") or {}
                if not isinstance(servers, dict) or not servers:
                    continue

                items = [s for s in servers.values() if isinstance(s, dict)]
                if not items:
                    continue

                server = next((s for s in items if s.get("type") == "stdio"), items[0])

                cmd = server.get("command")
                args = server.get("args", [])
                
                if isinstance(cmd, str):
                    if not isinstance(args, list):
                        args = []
                    args = [str(a) for a in args]
                    
                    # If it's a python command, wrap it with uv run
                    # Handles "python", "python3", or absolute paths like "C:\...\python.exe"
                    low_cmd = cmd.lower()
                    if low_cmd in ("python", "python3") or low_cmd.endswith("python.exe"):
                        return ["uv", "run", "python", *args]
                        
                    return [cmd, *args]
            except Exception:
                pass

    # 1) pyproject.toml (Python)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

            scripts = data.get("project", {}).get("scripts", {}) or {}
            poetry_scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {}) or {}

            merged: dict[str, Any] = {}
            if isinstance(scripts, dict):
                merged.update(scripts)
            if isinstance(poetry_scripts, dict):
                merged.update(poetry_scripts)

            entrypoint = _pick_entrypoint(merged)
            cmd = _command_from_entrypoint(entrypoint)
            if cmd:
                return cmd
        except Exception:
            pass

    # 2) package.json (Node)
    package_json = root / "package.json"
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text(encoding="utf-8"))
            scripts = pkg.get("scripts", {}) or {}
            if isinstance(scripts, dict):
                if "start" in scripts:
                    return ["npm", "run", "start"]
                if "dev" in scripts:
                    return ["npm", "run", "dev"]
        except Exception:
            pass

    return None