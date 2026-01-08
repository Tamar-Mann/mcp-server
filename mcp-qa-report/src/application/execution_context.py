"""
Execution context passed through all checks.

Holds target project_path, optional explicit start command,
timeout, and optional RunnerFactory override (useful for tests).
"""
from dataclasses import dataclass

from infrastructure.runner_factory import RunnerFactory

@dataclass(frozen=True)
class ExecutionContext:
    project_path: str
    command: list[str] | None = None
    timeout_sec: int = 5
    runner_factory: RunnerFactory | None = None

