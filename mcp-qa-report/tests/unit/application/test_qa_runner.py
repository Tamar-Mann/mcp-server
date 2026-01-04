from application.qa_runner import QARunner
from domain.models import CheckResult, CheckStatus
from application.policies import FailFastPolicy, RunAllPolicy


class _Check:
    def __init__(self, name: str, status: CheckStatus):
        self.name = name
        self._status = status

    def run(self, ctx):
        return CheckResult(self.name, self._status, f"{self.name} msg")


def test_qa_runner_run_all_policy_runs_all_checks():
    checks = [_Check("c1", CheckStatus.PASS), _Check("c2", CheckStatus.FAIL), _Check("c3", CheckStatus.PASS)]
    runner = QARunner(checks, RunAllPolicy())

    res = runner.run(ctx=object())
    assert [r.name for r in res] == ["c1", "c2", "c3"]


def test_qa_runner_fail_fast_stops_on_fail():
    checks = [_Check("c1", CheckStatus.PASS), _Check("c2", CheckStatus.FAIL), _Check("c3", CheckStatus.PASS)]
    runner = QARunner(checks, FailFastPolicy())

    res = runner.run(ctx=object())
    assert [r.name for r in res] == ["c1", "c2"]
