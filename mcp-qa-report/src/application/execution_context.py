from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionContext:
    project_path: str
    command: list[str] | None = None
    timeout_sec: int = 5


""" env: dict[str, str] | None
cwd: Path | None"""

