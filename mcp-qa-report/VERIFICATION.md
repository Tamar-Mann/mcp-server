# Verification (Codex / MCP Inspector)

The following scenarios were manually validated end-to-end using Codex and the MCP Inspector.

1. **Self-check without explicit command**  
   Auto-detection is attempted. When it is not possible, the tool fails fast with a clear error.

2. **Self-check with explicit command**  
   Providing `python -m mcp_server.server` results in a successful run with all checks passing.

3. **Tool discovery and description validation**  
   Tools are discovered correctly; missing descriptions are reported as warnings.

4. **Tool invocation with `ping` present**  
   Invocation succeeds via `tools/call`.

5. **Tool invocation without `ping`**  
   Invocation check is skipped with a warning (graceful degradation).

6. **Report output to directory**  
   Report is written successfully to `out/qa_report.txt`.

7. **Report output to explicit file path**  
   Report is written successfully to the requested file (e.g. `out/report.md`).

8. **Invalid output path (path traversal attempt)**  
   Write is rejected safely; execution continues and the report is returned inline.
