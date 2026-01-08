"""
Renders QA results as a human-readable checklist.

Each check is rendered on a single line with a status icon (PASS/WARN/FAIL),
followed by a short summary footer.
"""
import json
from domain.models import CheckResult, CheckStatus

class TextReporter:
    """
    Renders a list of CheckResult objects as a plain-text checklist report.
    """
    def render(self, results: list[CheckResult]) -> str:
        lines = []

        for r in results:
            status = r.status.value
            lines.append(f"{status} {r.name}")
            lines.append(f"   ↳ {r.message}")

        summary = self._summary(results)
        return "\n".join(lines + ["", summary])

    def to_json_obj(self, results: list[CheckResult]) -> dict:
        return {
            "summary": self._summary_obj(results),
            "results": [
                {
                    "name": r.name,
                    "status": r.status.name,
                    "message": r.message,
                }
                for r in results
            ],
        }

    def render_json(self, results: list[CheckResult]) -> str:
        return json.dumps(self.to_json_obj(results), ensure_ascii=False, indent=2)

    def _summary_obj(self, results: list[CheckResult]) -> dict:
        passed = sum(1 for r in results if r.status == CheckStatus.PASS)
        failed = sum(1 for r in results if r.status == CheckStatus.FAIL)
        warned = sum(1 for r in results if r.status == CheckStatus.WARN)
        return {"passed": passed, "warnings": warned, "failed": failed}

    def _summary(self, results: list[CheckResult]) -> str:
        s = self._summary_obj(results)
        return f"Summary: {s['passed']} passed, {s['warnings']} warnings, {s['failed']} failed"
