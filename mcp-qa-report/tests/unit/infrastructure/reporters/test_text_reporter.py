from domain.models import CheckResult, CheckStatus
from infrastructure.reporters.text_reporter import TextReporter


def test_text_reporter_summary_counts():
    results = [
        CheckResult("a", CheckStatus.PASS, "ok"),
        CheckResult("b", CheckStatus.WARN, "meh"),
        CheckResult("c", CheckStatus.FAIL, "no"),
    ]
    rep = TextReporter()
    s = rep.render(results)
    assert "Summary: 1 passed, 1 warnings, 1 failed" in s


def test_text_reporter_json_shape():
    results = [CheckResult("a", CheckStatus.PASS, "ok")]
    rep = TextReporter()
    obj = rep.to_json_obj(results)

    assert obj["summary"]["passed"] == 1
    assert obj["results"][0]["status"] == "PASS"
    assert obj["results"][0]["name"] == "a"
