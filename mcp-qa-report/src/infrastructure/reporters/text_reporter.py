from domain.models import CheckResult, CheckStatus

class TextReporter:
    def render(self, results: list[CheckResult]) -> str:
        lines = []

        for r in results:
            status = r.status
            lines.append(f"{status} {r.name}")
            lines.append(f"   ↳ {r.message}")

        summary = self._summary(results)
        return "\n".join(lines + ["", summary])

    def _summary(self, results: list[CheckResult]) -> str:
        passed = sum(1 for r in results if r.status == CheckStatus.PASS)
        failed = sum(1 for r in results if r.status == CheckStatus.FAIL)
        warned = sum(1 for r in results if r.status == CheckStatus.WARN)

        return f"Summary: {passed} passed, {warned} warnings, {failed} failed"
