# application/policies.py
from domain.models import CheckStatus

class FailFastPolicy:
    def should_stop(self, status: CheckStatus) -> bool:
        return status == CheckStatus.FAIL

class RunAllPolicy:
    def should_stop(self, status: CheckStatus) -> bool:
        return False
