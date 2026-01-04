# MCP QA Report (Local MCP Server)

A local **Model Context Protocol (MCP)** server that provides a single, practical tool:

- **`qa_report`** — run sanity checks against an MCP project (including *this* repo or any other local MCP project) and return a clear ✅/⚠️/❌ checklist report.

This project was built as an MCP implementation exercise and as a “self-check” utility for quickly validating MCP servers during development or review.

Built with reviewers in mind — because humans review a lot of MCP projects. `qa_report` compresses the essentials into a quick ✅/⚠️/❌ checklist.


---

## What this MCP does

`qa_report()` runs a small battery of protocol-level checks, for example:

- Server starts and responds over **STDIO**
- STDIO integrity (no noise before `initialize`)
- Tools are registered and discoverable (`tools/list`)
- Tool metadata quality (description presence/quality)
- Optional end-to-end tool invocation smoke test (`tools/call`), when a safe tool is available

The output is intentionally **a checklist**, not a score.

---

## Repository layout

The actual Python package lives under `mcp-qa-report/`:

```
mcp-qa-report/
  pyproject.toml
  src/
    mcp_server/           # MCP server entrypoint + tools
    application/          # orchestration (runner, policies)
    domain/               # ports + models
    infrastructure/       # checks, process runner, json-rpc client, reporters
  tests/                  # unit / integration / e2e
```

Design highlights (intentionally “clean architecture”-ish):

- **Single Responsibility**: checks, runner, reporters, and process/JSON-RPC plumbing are separated.
- **Dependency Inversion**: the runner depends on `QACheck` / `Reporter` protocols; infrastructure implements them.
- **Open/Closed**: add a new check by implementing `QACheck` and wiring it in `application/container.py`.

---

## Requirements

- Python **3.11+**
- Node.js (only for running the Inspector UI)

---

## Install (recommended)

From the repository root:

### Windows PowerShell
```powershell
cd mcp-qa-report
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
```

### macOS / Linux (bash/zsh)
```bash
cd mcp-qa-report
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

> Alternative: you can also run without installing by setting `PYTHONPATH=src`, but editable install is the cleanest way to avoid import issues.

---

## Run the MCP server (stdio)

After installation, run:

```bash
python -m mcp_server.server
```

The server logs to **stderr** (so it does not break MCP stdio JSON-RPC traffic).

---

## Use with MCP Inspector

1) Start the Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2) In the Inspector UI, create a **STDIO** server connection:

- **Command**: `python`
- **Args**: `-m mcp_server.server`
- **Working directory**: point it to the `mcp-qa-report` folder (recommended)

3) Connect, then open **Tools** and call **`qa_report`**.

### Inspector inputs for `qa_report`

- `project_path` (string, default `"."`):
  - Path to the target project you want to validate.
  - `"."` means “the server process working directory”.
- `command` (array of strings, optional):
  - How to start the *target* MCP server you are checking.
  - Leave **null** to auto-detect via:
    - `.vscode/mcp.json` or `mcp.json`
    - `pyproject.toml` scripts
    - `package.json` scripts (`start` / `dev`)
- `fail_fast` (bool, default `true`):
  - `true`: stop on first ❌ (faster).
  - `false`: run all checks and aggregate results.
- `output_path` (string, optional):
  - If omitted: returns the report text in the tool response.
  - If provided:
    - Directory mode (ends with `/` or `\` or has no suffix): writes `qa_report.txt` into that directory.
      - Example: `out/` or `out\`
    - File mode (has an extension): writes exactly to that file.
      - Example: `out/report.md`

---

## Example prompts for coding agents

Use these as “copy/paste” prompts for Cursor / Claude Code / Codex / Gemini, etc.

### Validate the current project (self-check)
> Run the `qa_report` tool with `project_path="."` and `fail_fast=false`. Summarize any ⚠️/❌ items and propose fixes with minimal code changes.

### Validate another local MCP project
> Run `qa_report` on `project_path="C:\path\to\other-mcp"` with `command=null` (auto-detect). If detection fails, retry with an explicit `command` array. Return the full checklist and the top 3 improvements.

### Persist a report file
> Run `qa_report` with `output_path="out/"` so the report is written to disk. Then explain where it was written and how to interpret the results.

---

## Tests

This project uses **pytest** and groups tests into three levels:

- **Unit tests** (default): fast tests that do not spawn subprocesses.
- **Integration tests** (`@pytest.mark.integration`): start a real MCP server subprocess and validate core protocol calls (`initialize`, `tools/list`).
- **E2E tests** (`@pytest.mark.e2e`): start a real MCP server subprocess and validate end-to-end tool invocation (`tools/call`, e.g. `ping`).

### Run unit tests (default)
```powershell
pytest -q
```

### Run integration tests (PowerShell)
```powershell
$env:RUN_INTEGRATION="1"
pytest -q -m integration
Remove-Item Env:RUN_INTEGRATION -ErrorAction SilentlyContinue
```

### Run E2E tests (PowerShell)
```powershell
$env:RUN_E2E="1"
pytest -q -m e2e
Remove-Item Env:RUN_E2E -ErrorAction SilentlyContinue
```

### Windows CMD equivalents
```cmd
pytest -q
set RUN_INTEGRATION=1 && pytest -q -m integration
set RUN_E2E=1 && pytest -q -m e2e
```

### Notes
- By default, integration and e2e tests are skipped unless the corresponding environment variable is set.
- To see which tests were skipped and why:
```powershell
pytest -q -rs
```

---

## Extending the checks

Add a new check by implementing `QACheck` (see `domain/ports.py`) and wiring it into `application/container.py`.

Ideas:
- Verify README presence and required sections (run/install/Inspector/examples)
- Verify tool `inputSchema` structure more strictly
- Add optional lint/format checks (kept separate from protocol checks)
- Export JSON report alongside text output

---

## License

MIT (or your preferred license).
