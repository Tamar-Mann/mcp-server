from dataclasses import dataclass

from infrastructure.runner_factory import RunnerFactory


@dataclass(frozen=True)
class ExecutionContext:
    project_path: str
    command: list[str] | None = None
    timeout_sec: int = 5
    runner_factory: RunnerFactory | None = None

