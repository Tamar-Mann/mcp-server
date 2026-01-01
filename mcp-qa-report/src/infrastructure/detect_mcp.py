from pathlib import Path
import tomllib
import json

def detect_mcp_command(project_path: str) -> list[str] | None:
    root = Path(project_path)

    # 1. pyproject.toml (Python MCP)

    if (root / "pyproject.toml").exists():
        return ["uv", "run", "python", "-m", "weather"]
    
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        data = tomllib.loads(pyproject.read_text())
        scripts = data.get("project", {}).get("scripts", {})
        if "qa-report-mcp" in scripts:
            return ["python", "-m", "mcp_server.server"]

    # 2. package.json (Node MCP)
    package_json = root / "package.json"
    if package_json.exists():
        pkg = json.loads(package_json.read_text())
        scripts = pkg.get("scripts", {})
        if "start" in scripts:
            return ["npm", "run", "start"]
        


    return None
