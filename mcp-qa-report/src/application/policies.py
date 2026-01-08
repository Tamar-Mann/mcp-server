"""
Stop policies for the QA runner.

FailFastPolicy stops on first FAIL.
RunAllPolicy always continues (aggregates all results).
"""
from domain.models import CheckStatus

class FailFastPolicy:
    def should_stop(self, status: CheckStatus) -> bool:
        return status == CheckStatus.FAIL

class RunAllPolicy:
    def should_stop(self, status: CheckStatus) -> bool:
        return False
