from application.qa_runner import QARunner
from application.policies import FailFastPolicy, RunAllPolicy

from infrastructure.checks.process_checks import MCPServerStartupCheck
from infrastructure.checks.stdio_checks import STDIOIntegrityCheck
from infrastructure.checks.tool_checks import ToolsRegistrationCheck
from infrastructure.checks.tool_quality_checks import ToolDescriptionQualityCheck
from infrastructure.reporters.text_reporter import TextReporter
from infrastructure.checks.invocation_checks import ToolInvocationCheck
from domain.ports import Reporter


def build_checks():
    return [
        MCPServerStartupCheck(),
        STDIOIntegrityCheck(),
        ToolsRegistrationCheck(),
        ToolDescriptionQualityCheck(),
        ToolInvocationCheck(),
    ]


def build_policy(fail_fast: bool) :
    return FailFastPolicy() if fail_fast else RunAllPolicy()


def build_reporter() -> Reporter:
    return TextReporter()


def build_runner(fail_fast: bool) -> QARunner:
    return QARunner(build_checks(), build_policy(fail_fast))
