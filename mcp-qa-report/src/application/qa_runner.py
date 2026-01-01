from typing import Iterable
from domain.ports import QACheck, StopPolicy
from domain.models import CheckResult

class QARunner:
    def __init__(self, checks: Iterable[QACheck], policy: StopPolicy):
        self._checks = checks
        self._policy = policy

    def run(self, ctx) -> list[CheckResult]:
        results: list[CheckResult] = []
        for check in self._checks:
            result = check.run(ctx)
            results.append(result)
            if self._policy.should_stop(result.status):
                break
        return results
