from domain.models import CheckStatus, CheckResult


def test_check_status_values_are_ascii():
    assert CheckStatus.PASS.value == "PASS"
    assert CheckStatus.WARN.value == "WARN"
    assert CheckStatus.FAIL.value == "FAIL"


def test_check_result_dataclass():
    r = CheckResult("x", CheckStatus.PASS, "ok")
    assert r.name == "x"
    assert r.status == CheckStatus.PASS
    assert r.message == "ok"
