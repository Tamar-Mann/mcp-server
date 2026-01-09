from enum import Enum
from dataclasses import dataclass

class CheckStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
