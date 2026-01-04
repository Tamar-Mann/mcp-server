import os
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: runs real subprocess server smoke tests")
    config.addinivalue_line("markers", "e2e: end-to-end tool invocation tests")


def pytest_collection_modifyitems(config, items):
    run_integration = os.getenv("RUN_INTEGRATION") == "1"
    run_e2e = os.getenv("RUN_E2E") == "1"

    for item in items:
        if "integration" in item.keywords and not run_integration:
            item.add_marker(pytest.mark.skip(reason="Set RUN_INTEGRATION=1 to run integration tests"))
        if "e2e" in item.keywords and not run_e2e:
            item.add_marker(pytest.mark.skip(reason="Set RUN_E2E=1 to run e2e tests"))
