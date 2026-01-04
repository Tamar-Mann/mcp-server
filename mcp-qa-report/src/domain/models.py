from enum import Enum
from dataclasses import dataclass

class CheckStatus(str, Enum):
    PASS = "✅"
    WARN = "⚠️"
    FAIL = "❌"

@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
