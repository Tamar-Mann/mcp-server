from contextlib import asynccontextmanager
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

@pytest.fixture
def fake_session():
    from unittest.mock import AsyncMock
    session = AsyncMock()
    session.runner.stderr_tail = "fake stderr"
    session.__aenter__.return_value = session

    # Provide default return values for common client methods
    session.client.initialize.return_value = {"result": {"ok": True}}
    session.client.call.return_value = {"result": {"content": [{"type": "text", "text": "ok"}]}}

    return session


@pytest.fixture
def ctx_factory(fake_session):
    class SharedFakeFactory:
        @asynccontextmanager 
        async def create(self, *args, **kwargs):
            yield fake_session
    return SharedFakeFactory()