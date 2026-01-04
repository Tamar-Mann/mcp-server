from domain.models import CheckStatus, CheckResult


def test_check_status_values_are_emojis():
    assert CheckStatus.PASS.value == "✅"
    assert CheckStatus.WARN.value == "⚠️"
    assert CheckStatus.FAIL.value == "❌"


def test_check_result_dataclass():
    r = CheckResult("x", CheckStatus.PASS, "ok")
    assert r.name == "x"
    assert r.status == CheckStatus.PASS
    assert r.message == "ok"
