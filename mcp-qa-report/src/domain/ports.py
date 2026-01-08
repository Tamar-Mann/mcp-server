from typing import Protocol
from .models import CheckResult, CheckStatus

class QACheck(Protocol):
    name: str
    def run(self, ctx) -> CheckResult: ...

class Reporter(Protocol):
    def render(self, results: list[CheckResult]) -> str: ...


class StopPolicy(Protocol):
    def should_stop(self, status: CheckStatus) -> bool: ...