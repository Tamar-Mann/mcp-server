"""
Orchestrates executing QA checks asynchronously.

Runs checks concurrently using asyncio.gather,
collects CheckResult items, and respects a StopPolicy (fail-fast or run-all).
"""
import asyncio
from typing import Iterable
from domain.ports import QACheck, StopPolicy
from domain.models import CheckResult

class QARunner:
    """Executes a sequence of QACheck instances concurrently under a StopPolicy.""" 
    def __init__(self, checks: Iterable[QACheck], policy: StopPolicy):
        self._checks = list(checks)
        self._policy = policy

    async def run(self, ctx) -> list[CheckResult]:
        # 1. Create tasks for all checks
        tasks = {asyncio.create_task(check.run(ctx)): check for check in self._checks}
        final_results: list[CheckResult] = []
        
        try:
            # 2. Process results as they finish (Parallel execution)
            for coro in asyncio.as_completed(tasks.keys()):
                result = await coro
                final_results.append(result)
                
                # 3. Fail-Fast check: If policy says stop, cancel remaining tasks
                if self._policy.should_stop(result.status):
                    for t in tasks.keys():
                        if not t.done():
                            t.cancel()
                    break
        except Exception as e:
            # Handle unexpected errors during execution
            for t in tasks.keys():
                t.cancel()
            raise e
            
        return final_results